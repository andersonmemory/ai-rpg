import os

import json
from dotenv import load_dotenv
from groq import Groq
import random

MODEL = "openai/gpt-oss-20b"
# MODEL = "qwen/qwen3.6-27b"

load_dotenv()
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

messages = []


class Player:
    """Object representing the AI agent"""

    def __init__(self, name, instructions):
        self.name = name
        self.instruction = instructions
        self.messages = [{"role": "system", "content": instructions}]

    def answer(self):
        output = []

        stream = client.chat.completions.create(
            messages=self.messages,
            model=MODEL,
            stream=True,
            reasoning_format="hidden",
            max_tokens=5000,
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

        if output:
            print()
            messages.append(
                {"role": "user", "content": f"[{self.name}]: {''.join(output)}"}
            )
            return "".join(output)
        else:
            print(f"ERROR: No content generated. Finish_reason: {finish_reason}")
            return
