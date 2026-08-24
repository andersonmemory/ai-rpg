import os

from dotenv import load_dotenv
from groq import Groq
import random

custom_instructions = """
    - Answer in plain text, in a continuous line, pure text. Natural way.
    - Few sentences, this is a game.
    - You're receiving the narration from a DM, and you are the player.
    - You have to decide as if you are the character.
"""

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


def read(input):

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{custom_instructions} {input}",
            }
        ],
        model="qwen/qwen3.6-27b",
        reasoning_format="hidden",
    )

    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


def read_stream(input):

    output_text = []
    stream = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{custom_instructions} {input}",
            }
        ],
        model="qwen/qwen3.6-27b",
        stream=True,
        reasoning_format="hidden",
    )

    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            print(text, end="", flush=True)
            output_text.append(text)

    print()
    return "".join(output_text)


# TODO: have your own tools.py file for modularity with some .json loading
# TODO: executes tool call and prints the content once it's finished
def read_stream_call():
    # TODO: initialize message
    # TODO: tool schema
    # returns the final content
    pass


# TODO: executes tool call and streams the content
def read_stream_call(input):
    # initialize message
    messages = [
        {"role": "system", "content": custom_instructions},
        {"role": "user", "content": input},
    ]

    # return printed chunks with flush enabled
    # return list containing all chunks together
    pass


# Tool map:
available_functions = {"roll_d6": roll_d6}

# Tool definitions:
roll_d6 = {
    "type": "function",
    "function": {
        "name": "roll_d6",
        "description": "rolls a d6 dice, only use if it is asked to perform a test",
    },
}


# Function definition:
def roll_d6():
    return random.randint(1, 6)
