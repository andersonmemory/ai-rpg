from google import genai
from pathlib import Path

from dotenv import load_dotenv
import os

env_path =Path.cwd().parent.resolve() / ".env"

load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=GEMINI_API_KEY)


response = client.models.generate_content(
    model="gemini-2.5-flash", 
    contents="Explain how AI works in a few words"
)

print(response.text)