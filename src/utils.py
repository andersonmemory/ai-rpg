import os

import json
from dotenv import load_dotenv
from groq import Groq
import random

MODEL = "qwen/qwen3.6-27b"

custom_instructions = """
    - Answer in plain text, brazilian portuguese, in a continuous line, pure text. Natural way.
    - Few sentences, this is a game.
    - You're receiving the narration from a DM, and you are the player.
    - You have to decide as if you are the character.
"""

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# shared memory
messages = [
    {"role": "system", "content": custom_instructions},
]


def read_stream(input):

    output = []

    # initialize message
    messages.append(
        {
            "role": "user",
            "content": f" {input}",
        }
    )

    stream = client.chat.completions.create(
        messages=messages,
        model=MODEL,
        stream=True,
        reasoning_format="hidden",
    )

    finish_reason = None

    for chunk in stream:
        if chunk.choices[0].delta.content:
            output.append(chunk.choices[0].delta.content)
            print(chunk.choices[0].delta.content, end="", flush=True)
        if chunk.choices[0].finish_reason == "stop":
            finish_reason = "stop"

    if finish_reason == "stop":
        print()
        messages.append({"role": "assistant", "content": "".join(output)})
        return "".join(output)
    else:
        print(f"ERROR: Unknown finish_reason: {finish_reason}")
