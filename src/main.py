import requests

from murf import Murf
import requests

from subprocess import run
from shlex import split

from google import genai

from pathlib import Path

from dotenv import load_dotenv
import os

env_path = Path.cwd().parent.resolve() / ".env"

load_dotenv(dotenv_path=env_path)

GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")


# The client gets the API key from the environment variable `GEMMA_API_KEY`.
gemma_client = genai.Client(api_key=GEMMA_API_KEY)
murf_client = Murf(api_key=MURF_API_KEY)


def main():

    while True:
    
        # prompt = str(input("Diga o que ocorre: "))
        # prompt = "Rosas são vermelhas... continue, e seja curto, sem dizer mais nada além disso."

        user_info = input("Diga o que ocorre:")

        prompt = """Você é um boneco de jogo de rpg em jogo de aventura. Um mestre está narrando
        e você só reage aos eventos""" + user_info + """
        """ + """(seja curto, mas nem tanto e lembre-se que é uma fala de um personagem em tom coloquial, 
        mas não faça de propósito nem coloque jargões ou repetições, entre no personagem e reaja de uma forma
        como ele realmente iria se sentir nessa situação)"""

        response = gemma_client.models.generate_content(
            model="gemma-3-27b-it",
            contents=prompt,
        )

        new_generated_text = response.text

        audio_res = murf_client.text_to_speech.generate(
            text=new_generated_text,
            voice_id="Silvio"
        )

        print(audio_res.audio_file)

        request = requests.get(audio_res.audio_file)
        print(request)

        with open("file.wav", 'wb') as f:
            f.write(request.content)

        completed_process = run(split('vlc file.wav'))

        # TODO: add memory
        # with open() as fr:
        #     with open() as fw:

        # instruction = """Você está num rpg, e está sintetizando uma sequência de ações para conseguir
        # lembrar dos eventos, pois uma IA vai usar esse mesmo texto para conseguir se basear para lembrar
        # quem é e continuar as ações seguintes. Isso inclui contexto como conversa, personagens, e outras informações.
        
        # Tente sintetizar o máximo que consegue, mas apenas o essencial, de modo que se for a primeira vez que se lê
        # esse texto é possível entender o que está ocorrendo e continuar a história a partir desse ponto sem
        # perder informações importantes."""

        # response2 = client.models.generate_content(
        #     model="gemma-3-27b-it",
        #     contents=instruction,
        # )


if __name__ == '__main__':
    main()

