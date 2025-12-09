# This file is going to create the players
from google import genai

from pathlib import Path

from dotenv import load_dotenv
import os
import sys
import time

env_path = Path.cwd().parent.resolve() / ".env"

load_dotenv(dotenv_path=env_path)

GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")

client = genai.Client(api_key=GEMMA_API_KEY)

# game_system = None
player_creator = None
game_introduction = None


def main():

    if not len(sys.argv) == 2:
        print("Usage: python player_creator.py <output.txt>")
        sys.exit()

    output_filename = sys.argv[1]

    # Asks for user's basic description for the character.
    basic_description = input("Diga uma leve descrição de como quer que seja o personagem: ")

    global game_introduction
    global initiative_value
    initiative_value = input("Iniciativa: ")

    initiative_text = f"""\n\n### Iniciativa ###

    Valor de iniciativa: {initiative_value}"""

    prompt = player_creator + basic_description + initiative_text + game_introduction 

    # Insert the prompt to the AI
    response = client.models.generate_content(model="gemma-3-27b-it", contents=prompt)

    with open(f"characters/{output_filename}", 'w') as f:
        f.write(response.text)


if __name__ == '__main__':

    with open("settings/player_creator_prompt.txt", 'r') as f:
        player_creator = f.read() 

    with open("settings/game_introduction.txt", 'r') as f:
       game_introduction = f.read() 

    start = time.perf_counter()
    main()
    end = time.perf_counter()
    time_elapsed = end - start
    print("✅ Success. \n⏱️ Time taken: {time_elapsed:.06f}") 