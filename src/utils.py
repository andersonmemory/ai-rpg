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
    - When asked by the DM roll the die using roll_d6 and say out your result.
    - You're responsible for your own dice rolls.

    What to do when executing a dice roll:
    > State what value you got and wait for the next response. Its the DM job
    to narrate what happens next based on your result.

    Example: 
    DM: Do a test check 
    AI: It's a 6
"""

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# shared memory
messages = [
    {"role": "system", "content": custom_instructions},
]


# TODO: have your own tools.py file for modularity with some .json loading
def read_stream_call(input):
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
        tools=[roll],
        tool_choice="auto",
        stream=True,
        reasoning_format="hidden",
    )

    # initialize variables
    output = []
    tool_calls = []
    finish_reason = None

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            output.append(chunk.choices[0].delta.content)

        if chunk.choices[0].delta.tool_calls:
            tool_calls.extend(chunk.choices[0].delta.tool_calls)

        if chunk.choices[0].finish_reason == "stop":
            finish_reason = "stop"
        elif chunk.choices[0].finish_reason == "tool_calls":
            finish_reason = "tool_calls"

    if tool_calls:
        messages.append(
            {"role": "assistant", "content": "".join(output), "tool_calls": tool_calls}
        )
    else:
        messages.append({"role": "assistant", "content": "".join(output)})

    if finish_reason == "stop":
        print()
        return "".join(output)

    elif finish_reason == "tool_calls":
        messages.extend(execute_tools(tool_calls))

        stream_call = client.chat.completions.create(
            messages=messages, model=MODEL, stream=True, reasoning_format="hidden"
        )

        final_output = []

        for chunk in stream_call:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                final_output.append(chunk.choices[0].delta.content)

            if chunk.choices[0].finish_reason == "stop":
                print()
                messages.append({"role": "assistant", "content": "".join(final_output)})
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
        if not tool_call.function or not tool_call.function.name:
            continue

        id = tool_call.id
        name = tool_call.function.name
        function = tool_map[name]
        result = function()
        tools.append(
            {"role": "tool", "content": result, "tool_call_id": id, "name": name}
        )
    return tools
