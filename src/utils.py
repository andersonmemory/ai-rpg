import os

import json
from dotenv import load_dotenv
from groq import Groq
import random

MODEL = "qwen/qwen3.6-27b"

custom_instructions = """
    - Answer in plain text, in a continuous line, pure text. Natural way.
    - Few sentences, this is a game.
    - You're receiving the narration from a DM, and you are the player.
    - You have to decide as if you are the character.
    - When asked by the DM roll the die using roll_d6 and say out your result.
    - You're responsible for your own dice rolls.
"""

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


# TODO: have your own tools.py file for modularity with some .json loading
# TODO: executes tool call and prints the content once it's finished
# TODO: executes tool call and streams the content
def read_stream_call(input):
    # initialize message
    messages = [
        {"role": "system", "content": custom_instructions},
        {"role": "user", "content": input},
    ]
    stream = client.chat.completions.create(
        messages=messages, model=MODEL, tools=[roll], tool_choice="auto", stream=True
    )

    # initialize variables
    final_output = []
    tool_calls = []

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            final_output.append(chunk.choices[0].delta.content)

        if chunk.choices[0].delta.tool_calls:
            tool_calls = chunk.choices[0].delta.tool_calls

        if chunk.choices[0].finish_reason == "stop":
            print()
            return "".join(final_output)
        elif chunk.choices[0].finish_reason == "tool_calls":
            messages.extend(execute_tools(tool_calls))

            stream_call = client.chat.completions.create(
                messages=messages, model=MODEL, stream=True
            )

            for chunk in stream_call:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    final_output.append(chunk.choices[0].delta.content)

                if chunk.choices[0].finish_reason == "stop":
                    print()
                    return "".join(final_output)


# Function definition:
def roll_d6():
    return json.dumps(random.randint(1, 6))


# Tool map:
tool_map = {"roll_d6": roll_d6}

# Tool definitions:
roll = {
    "type": "function",
    "function": {
        "name": "roll_d6",
        "description": "rolls a d6 dice, only use if it is asked to perform a test",
    },
}


def execute_tools(tool_calls):
    tools = []
    for tool_call in tool_calls:
        id = tool_call.id
        name = tool_call.function.name
        function = tool_map[name]
        result = function()
        tools.append(
            {"role": "tool", "content": result, "tool_call_id": id, "name": name}
        )
    return tools
