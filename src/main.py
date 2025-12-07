from google import genai

from pathlib import Path

from dotenv import load_dotenv
import os

env_path = Path.cwd().parent.resolve() / ".env"

load_dotenv(dotenv_path=env_path)

GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")

# The client gets the API key from the environment variable `GEMMA_API_KEY`.
client = genai.Client(api_key=GEMMA_API_KEY)

response = client.models.generate_content(
    model="gemma-3-27b-it",
    contents="Roses are red...",
)

print(response.text)
