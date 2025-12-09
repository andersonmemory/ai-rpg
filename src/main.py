import requests
import os.path
from pathlib import Path
import asyncio

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


player1 = ""
player2 = ""

with open("player1.txt", 'r') as f:
    player1 = f.read()

with open("player2.txt", 'r') as f:
    player2 = f.read()

print(player1)
print(player2)


def history_maker(master_narration, player1_actions, player2_actions : str = "", history : str = ""):

    saving_message = f"""
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
                **Narração do Mestre:** {master_narration}
                **Última Resposta do Jogador 1:** {player1_actions}

                """

    if player2_actions:
        saving_message += """**Última Resposta do Jogador 2:** {player2_actions}
        ---"""

    if history:
        saving_message += f"""**O RESTO DO ARQUIVO INTEIRO DA HISTÓRIA ANTERIOR 
        (MODIFIQUE E ADAPTE COM AS NOVAS INFORMAÇÕES)**{history}"""

    return saving_message


async def main():

    if not os.path.exists(history_path):
        print("Não há nenhum arquivo de histórico, criando um.")

        with open("history.txt", "w") as fw:
                pass

    # DONE: fix problem: the AI players doesn't know who is who so they two think they are the player one.
    while True:

        # master's turn
        user_input = input("Diga o que ocorre: ")

        # DONE: check if there is an history.txt file
        history = "" 

        with open("history.txt", 'r') as f:
           for line in f:
                print(line)
                history += f.readline()

        player1_prompt = f"""{player1} 
        Descrição dos eventos ocorridos:
        {history}"""

        player1_response = gemma_client.models.generate_content(
            model="gemma-3-27b-it",
            contents=player1_prompt,
        )

        player1_text = player1_response.text

        # Done: put player speak here
        await player_speak(1, player1_text)

        # TODO: fill here
        instruction_history = history_maker(user_input, player1_text) 

        history_saver_one_response = gemma_client.models.generate_content(
            model="gemma-3-27b-it",
            contents=instruction_history,
        )

        history_saver_one_text = history_saver_one_response.text

        with open("history.txt", 'a') as f:
            f.write(f"\n{history_saver_one_text}")

        player2_prompt = f"""{player2} 
        Descrição dos eventos ocorridos:
        {history_saver_one_text}"""

        player2_response = gemma_client.models.generate_content(
            model="gemma-3-27b-it",
            contents=player2_prompt + "É sua vez de agir agora, o turno é seu.",
        )

        history = ""
        # TODO: is this necessary since we have line 152?
        with open("history.txt", 'r') as f:
             for line in f:
                  history += f.readline()

        player2_text = player2_response.text

        # TODO: AI player 2 
        await player_speak(2, player2_text)

        instruction = history_maker(user_input, player1_text, player2_text, history=history)

        final_definitive_history_file_response = gemma_client.models.generate_content(
            model="gemma-3-27b-it",
            contents=instruction,
        )

        final_definitive_history_file_text = final_definitive_history_file_response.text
        print(final_definitive_history_file_text)

        os.remove("history.txt")

        with open("history.txt", 'w') as f:
            f.write(f"\n{final_definitive_history_file_text}")


async def player_speak(player : int, message : str):

        if player == 1:

            audio_res = murf_client.text_to_speech.generate(
            text=message,
            voice_id="Silvio"
            )

            duration_in_seconds = audio_res.audio_length_in_seconds

            print(f"duração do áudio é: {duration_in_seconds}")

            request = requests.get(audio_res.audio_file)

            with open("file.wav", 'wb') as f:
                f.write(request.content)

            run(split('cvlc file.wav'))
            # await asyncio.sleep(duration_in_seconds)
            return

        elif player == 2:
            audio_res = murf_client.text_to_speech.generate(
            text=message,
            voice_id="Gustavo"
            )

            duration_in_seconds = audio_res.audio_length_in_seconds

            print(f"duração do áudio é: {duration_in_seconds}")

            request = requests.get(audio_res.audio_file)

            with open("file2.wav", 'wb') as f:
                f.write(request.content)

            run(split('cvlc file2.wav'))
            # await asyncio.sleep(duration_in_seconds)
            return

if __name__ == '__main__':
    asyncio.run(main())

