import os

import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.environ.get("MODEL", "gpt-4o-mini")
MODEL_SUMMARIZER = os.environ.get("MODEL_SUMMARIZER", MODEL)

MAX_MESSAGES = 10

client = OpenAI(
    api_key=os.environ.get("API_KEY")
    or os.environ.get("OPENAI_API_KEY")
    or os.environ.get("GROQ_API_KEY")
    or os.environ.get("GEMINI_API_KEY"),
    base_url=os.environ.get("BASE_URL"),
)

global_messages = []
global_history = ""


THINKING_TAGS = [
    ("<think>", "</think>"),
    ("<thought>", "</thought>"),
    ("<tool_call>", "</tool_call>"),
]


def strip_thinking_tags(text: str) -> str:
    """Remove thinking/tool_call blocks from a complete string."""
    for open_tag, close_tag in THINKING_TAGS:
        while open_tag in text:
            start = text.find(open_tag)
            end = text.find(close_tag, start)
            if end == -1:
                text = text[:start]
            else:
                text = text[:start] + text[end + len(close_tag) :]
    return text.strip()


def extract_json(text: str) -> str | None:
    """Extract the first complete JSON object from text by tracking brace depth."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


class Player:
    """Object representing the AI agent"""

    def __init__(self, name, instructions, raw_instructions=""):
        self.name = name
        self.instruction = instructions
        self.raw_instructions = raw_instructions

    def answer(self):
        output = []

        global_messages.insert(0, {"role": "system", "content": self.instruction})

        stream = client.chat.completions.create(
            messages=global_messages, model=MODEL, stream=True, tool_choice="none"
        )

        finish_reason = None
        in_block = False
        print(f"{self.name}: ", end="", flush=True)

        for chunk in stream:
            content = chunk.choices[0].delta.content

            if content:
                for open_tag, close_tag in THINKING_TAGS:
                    if open_tag in content:
                        in_block = True
                        content = content.split(open_tag)[0]
                    if close_tag in content:
                        in_block = False
                        content = content.split(close_tag)[-1]

                if content and not in_block:
                    output.append(content)
                    print(content, end="", flush=True)

            if chunk.choices[0].finish_reason is not None:
                finish_reason = chunk.choices[0].finish_reason

        print("\n")
        output = "".join(output)
        global_messages.pop(0)

        if output:
            global_messages.append(
                {"role": "user", "content": f"[{self.name}]: {output}"}
            )
            return output
        else:
            print(f"ERROR: No content generated. Finish_reason: {finish_reason}")
            return


def summarize():
    global global_history
    global global_messages

    messages = [
        {
            "role": "system",
            "content": "Você é um sumarizador de sessões de RPG. Dado o resumo anterior e essas mensagens antigas, gere um novo resumo conciso de até 3 frases contendo apenas os fatos cruciais e o estado atual do ambiente.",
        },
        {"role": "user", "content": f"{global_history} ### {global_messages}"},
    ]

    response = client.chat.completions.create(messages=messages, model=MODEL_SUMMARIZER)

    summary = strip_thinking_tags(response.choices[0].message.content)
    if summary:
        global_history = summary

    global_messages[:] = global_messages[-3:]
    global_messages.insert(
        0, {"role": "user", "content": f"### Contexto da situação: {global_history}"}
    )

    return global_history


def generate_character(theme: str) -> list:
    """Generate 3 unique Player objects based on the DM's opening prompt."""
    created = []
    max_attempts = 9

    while len(created) < 3 and max_attempts > 0:
        max_attempts -= 1
        messages = [
            {
                "role": "system",
                "content": (
                    "Você cria personagens de RPG humanos e críveis. "
                    "Os nomes devem ser nomes comuns realistas, sem apelidos descritivos ou arquetípicos entre aspas (ex: evite 'João \"O Corajoso\" Silva'). "
                    "As personalidades devem ser nuançadas: um traço dominante existe, mas não é absoluto — uma pessoa engraçada sabe quando parar de brincar, um líder às vezes hesita, um cético pode se surpreender. "
                    "Os personagens são seres humanos com instinto de sobrevivência — mesmo os impulsivos não agem de forma suicida. "
                    "O contraste entre personagens aparece no estilo, postura e prioridades, não em comportamentos impossíveis. "
                    "Responda SOMENTE com JSON puro, sem texto adicional, sem markdown, sem explicações. "
                    "Formato obrigatório: {\"name\": \"<nome>\", \"instructions\": \"<frase curta em português descrevendo a personalidade e como o personagem age em 1ª pessoa>\"}"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Tema: {theme}\n"
                    f"Personagens já criados (seja CONTRASTANTE com eles em personalidade e estilo de agir): "
                    f"{[{'nome': p.name, 'personalidade': p.raw_instructions} for p in created]}\n"
                    "Crie um novo personagem único. Responda apenas com o JSON."
                ),
            },
        ]

        response = client.chat.completions.create(
            messages=messages, model=MODEL_SUMMARIZER
        )

        raw = response.choices[0].message.content

        try:
            # Strip thinking tags first, then extract JSON from the clean text
            clean = strip_thinking_tags(raw)
            json_str = extract_json(clean)
            if not json_str:
                continue
            data = json.loads(json_str)
            # Append the response format constraint so agents always reply in 1 sentence
            instruction = (
                f"Português do Brasil.\n"
                f"Você é {data['name']}. Responda APENAS como {data['name']}. Nunca responda por outros personagens.\n"
                f"{data['instructions']}\n"
                f"### Aja sempre como um ser humano realista com instinto de sobrevivência. Mesmo sendo impulsivo ou agressivo, nunca tome ações obviamente suicidas (como atacar guardas armados a mãos nuas).\n"
                f"### Adapte o tom à gravidade da situação: em perigo real, humor e frieza cedem lugar ao medo ou urgência; sua personalidade molda como reage, não anula o que sente.\n"
                f"### Máximo de 1 frase em 1ª pessoa. Pode ser uma ação, um diálogo direto com outro personagem pelo nome, ou ambos.\n"
                f"### Nunca use o formato [Nome]: na sua resposta. Escreva apenas a frase diretamente.\n"
                f"### Reaja somente ao que está fisicamente presente na cena descrita pelo DM. Se o DM menciona algo em um papel, é apenas informação, não uma presença física.\n"
                f"### Deve ser obrigatoriamente na mesma linha."
            )
            player = Player(data["name"], instruction, data["instructions"])
            created.append(player)
        except (json.JSONDecodeError, KeyError):
            continue

    return created
