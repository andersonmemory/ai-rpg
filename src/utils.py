import os

from dotenv import load_dotenv
from google import genai

custom_instructions = """
    - Answer in plain text, in a continuous line, pure text. Natural way.
"""

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def read(input):

    interaction = client.interactions.create(
        model="gemma-4-26b-a4b-it", input=f"{custom_instructions} {input}"
    )
    print(interaction.output_text)
    return interaction.output_text


def read_stream(input):

    output_text = []

    stream = client.interactions.create(
        model="gemma-4-26b-a4b-it",
        input=f"{custom_instructions} {input}",
        stream=True,
    )
    for event in stream:
        if event.event_type == "step.delta":
            if event.delta.type == "text":
                print(event.delta.text, end="", flush=True)
                output_text.append(event.delta.text)

    print()
    return "".join(output_text)
