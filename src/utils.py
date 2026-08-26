import os

import json
from dotenv import load_dotenv
from groq import Groq
import random


MODEL = "openai/gpt-oss-120b"
MODEL_SUMMARIZER = "openai/gpt-oss-20b"
# MODEL = "qwen/qwen3.6-27b"

MAX_MESSAGES = 10

load_dotenv()
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
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

        global_messages.insert(0, {"role": "user", "content": self.instruction})

        stream = client.chat.completions.create(
            messages=global_messages,
            model=MODEL,
            stream=True,
            reasoning_format="hidden",
        )

        finish_reason = None
        print(f"{self.name}: ", end="", flush=True)

        for chunk in stream:
            if chunk.choices[0].delta.content:
                output.append(chunk.choices[0].delta.content)
                print(chunk.choices[0].delta.content, end="", flush=True)
            if chunk.choices[0].finish_reason != None:
                finish_reason = chunk.choices[0].finish_reason

        output = "".join(output)
        global_messages.pop(0)

        if output:
            print()
            global_messages.append(
                {"role": "user", "content": f"[{self.name}]: {''.join(output)}"}
            )
            return "".join(output)
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

    response = client.chat.completions.create(
        messages=messages, model=MODEL_SUMMARIZER, reasoning_format="hidden"
    )

    global_history = response.choices[0].message.content

    global_messages[:] = global_messages[-3:]
    global_messages.insert(
        0, {"role": "user", "content": f"### Contexto da situação: {global_history}"}
    )

    return response.choices[0].message.content
