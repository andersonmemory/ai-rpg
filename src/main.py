import requests
import os.path
from pathlib import Path

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

history_path = Path.cwd().resolve() / "history.txt"


# The client gets the API key from the environment variable `GEMMA_API_KEY`.
gemma_client = genai.Client(api_key=GEMMA_API_KEY)
murf_client = Murf(api_key=MURF_API_KEY)


def main():

    if not os.path.exists(history_path):
        print("Não há nenhum arquivo de histórico, criando um.")

        with open("history.txt", "w") as fw:
                pass

    while True:
    
        user_input = input("Diga o que ocorre:")

        # TODO: check if there is an history.txt file

        prompt = """Você é um boneco de jogo de rpg em jogo de aventura. Um mestre está narrando
        e você só reage aos eventos""" + user_input + """
        """ + """(seja curto, mas nem tanto e lembre-se que é uma fala de um personagem em tom coloquial, 
        mas não faça de propósito nem coloque jargões ou repetições, entre no personagem e reaja de uma forma
        como ele realmente iria se sentir nessa situação)
        """

        history = "" 

        with open("history.txt", 'r') as f:
           for line in f:
                print(line)
                history += f.readline()


        prompt = f"""Você é um boneco de jogo de rpg em jogo de aventura. Um mestre está narrando
        e você só reage aos eventos""" + user_input + """
        """ + """(seja curto, mas nem tanto e lembre-se que é uma fala de um personagem em tom coloquial, 
        mas não faça de propósito nem coloque jargões ou repetições, entre no personagem e reaja de uma forma
        como ele realmente iria se sentir nessa situação, tente não falar de si em terceira pessoa ou repetir
        informações que o mestre diz, fale como se nem estivesse ouvindo o mestre e sim reagindo e que 
        tudo o que está sendo descrito são na verdade o que está ocorrendo e como você reage a isso)

        aqui está a sequência de eventos do que você ou outros realizaram até então e prossiga a partir
        disso (se não tiver nada aqui apenas faça o que foi pedido):
        {history}
        """

        response = gemma_client.models.generate_content(
            model="gemma-3-27b-it",
            contents=prompt,
        )

        new_generated_text = response.text

        audio_res = murf_client.text_to_speech.generate(
            text=new_generated_text,
            voice_id="Silvio"
        )

        request = requests.get(audio_res.audio_file)

        with open("file.wav", 'wb') as f:
            f.write(request.content)

        completed_process = run(split('cvlc file.wav'))

        instruction = f"""
            Você é um **Cronista da Aventura** com a tarefa de criar um resumo conciso e completo do histórico de jogo (session history).

            Este resumo servirá como base de memória para a continuidade da narrativa, devendo ser totalmente compreensível para qualquer um que o leia pela primeira vez, permitindo a retomada imediata da história a partir do ponto final.

            **INFORMAÇÕES ESSENCIAIS A INCLUIR NO RESUMO:**

            * **Contexto e Ambiente:** Onde o personagem está, como o local é (descrição, atmosfera - calmo, perigoso, etc.) e como ele chegou ali.
            * **Personagem:** Identidade, ferimentos recentes, estado de ânimo, habilidades relevantes usadas.
            * **Inventário/Recursos:** Itens importantes guardados ou usados recentemente.
            * **Interações:** NPCs encontrados, diálogos cruciais, pedidos de ajuda ou informações.
            * **Sequência de Ações:** O que foi feito, as últimas ações do personagem e a resposta do ambiente/Mestre a elas.

            **Sintetize o máximo, mantendo apenas o essencial para a continuidade da história.**

            **TEXTO COMPLETO A SER RESUMIDO E COMPACTADO:**
            ---
            **Narração do Mestre:** {user_input}
            **Última Resposta do Jogador:** {new_generated_text}
            ---
            """

        response2 = gemma_client.models.generate_content(
            model="gemma-3-27b-it",
            contents=instruction,
        )

        result = response2.text
        print(result)

        with open("history.txt", 'a') as f:
            f.write(f"\n{result}")


if __name__ == '__main__':
    main()

