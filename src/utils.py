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


class Player:
    """Object representing the AI agent"""

    def __init__(self, name, instructions):
        self.name = name
        self.instruction = instructions

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
                for open_tag, close_tag in [
                    ("<think>", "</think>"),
                    ("<thought>", "</thought>"),
                    ("<tool_call>", "</tool_call>"),
                ]:
                    if open_tag in content:
                        in_block = True
                        content = content.split(open_tag)[0]
                    if close_tag in content:
                        in_block = False
                        content = content.split(close_tag)[-1]

                if content and not in_block and content.strip():
                    output.append(content)
                    print(content, end="", flush=True)

            if chunk.choices[0].finish_reason is not None:
                finish_reason = chunk.choices[0].finish_reason

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

    global_history = response.choices[0].message.content

    global_messages[:] = global_messages[-3:]
    global_messages.insert(
        0, {"role": "user", "content": f"### Contexto da situação: {global_history}"}
    )

    return response.choices[0].message.content
