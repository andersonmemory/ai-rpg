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

import sys

env_path = Path.cwd().parent.resolve() / ".env"

load_dotenv(dotenv_path=env_path)

GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

# Data related
history_path = Path.cwd().resolve() / "history.txt"


# The client gets the API key from the environment variable `GEMMA_API_KEY`.
gemma_client = genai.Client(api_key=GEMMA_API_KEY)
murf_client = Murf(api_key=MURF_API_KEY)

class Player():
    def __init__(self, prompt):
        self.prompt = prompt


player1 = Player("")
player2 = Player("")

player_map = {
    1: player1,
    2: player2,
}


with open("player1.txt", 'r') as f:
    player1 = f.read()

with open("player2.txt", 'r') as f:
    player2 = f.read()

def history_maker(master_narration, player1_actions, player2_actions : str = "", history : str = ""):

    plot = None
    
    with open('data/plot.txt', 'r') as f:
        plot = f.read() 

    saving_message = f"""

                ### Instrução ###

                Função: você é um cronista da aventura com a tarefa de criar um 
                resumo conciso e completo do histórico de jogo (session history),
                utilizando os dados fornecidos da seção "dados".

                O resumo serve como memória para continuar a narrativa. Alguém que leia 
                pela primeira vez deve ser capaz de retomar a história a partir do ponto final de maneira imediata.

                A seção "descrição do trama deste jogo" serve para lhe dar contexto. Evite usar essa informação,
                a menos que veja pontos no resumo que são explícitos ou implicitos e estão ligados com a 
                intenção do personagem com a trama.
                
                ### Como se comportar ###

                evite fazer modificações de informações existentes a menos que isso deixe mais curta,
                sem sobrescrever. Escreva informações que recebeu, tornando mais curtas.

                Você vai adicionar nova informação em cima da que já lhe foi fornecida na seção
                "ARQUIVO INTEIRO DA HISTÓRIA ANTERIOR", apenas simplificando os atos anteriores, para
                construir uma narrativa contínua.

                Quando ler "jogador" entenda como personagens controláveis.

                ### Descrição do trama deste jogo ###

                {plot}

                ### Informações essenciais para incluir no resumo ### 

                Contexto e Ambiente: <Onde o personagem está, como o local é (descrição, atmosfera - calmo, perigoso, etc.) e como ele chegou ali>
                Personagens: <Identidade, ferimentos recentes, estado de ânimo, habilidades relevantes usadas; informações de ambos jogadores>
                Inventário/Recursos: <Itens importantes guardados ou usados recentemente; informações de ambos jogadores>
                Interações: <NPCs encontrados, diálogos cruciais, pedidos de ajuda ou informações; informações de ambos jogadores>.
                Sequência de Ações: <O que foi feito, as últimas ações dos dois jogadores e a resposta do ambiente/Mestre a elas>.
                
                Presente: <último diálogo, última ação realizada, e o que cada um dos dois personagens está pensando até o momento>

                Sintetize o máximo, mantendo apenas o essencial para a continuidade da história.

                ### Dados ###
                Narração do Mestre: {master_narration}
                Última Resposta do Jogador 1: {player1_actions}

                """

    if player2_actions:
        saving_message += """**Última Resposta do Jogador 2:** {player2_actions}
        ---"""

    if history:
        saving_message += f"""
        
        ### O ARQUIVO INTEIRO DA HISTÓRIA ANTERIOR ###
        ### MODIFIQUE E ADAPTE COM AS NOVAS INFORMAÇÕES ###
        
        Arquivo: <caso ler nada após essa linha, ignore> {history}"""

    return saving_message


async def main():

    if not len(sys.argv) == 3:
        print("Usage: python main.py <./path/to/player1.txt> <./path/to/player2.txt>")

    player1 = sys.argv[1]
    player2 = sys.argv[2]

    if not os.path.exists(history_path):
        print("Não há nenhum arquivo de histórico, criando um.")

        with open("history.txt", "w") as fw:
                pass

    # DONE: fix problem: the AI players doesn't know who is who so they two think they are the player one.
    while True:

        # master's turn
        user_input = input("Diga o que ocorre: ")


async def player_speak(player : int, message : str):

        voice_hashmap = {
            1: "Silvio",
            2: "Gustavo",
        }

        audio_res = murf_client.text_to_speech.generate(
        text=message,
        voice_id=voice_hashmap[player]
        )

        duration_in_seconds = audio_res.audio_length_in_seconds

        print(f"duração do áudio é: {duration_in_seconds}")

        request = requests.get(audio_res.audio_file)

        with open(f"file{player}.wav", 'wb') as f:
            f.write(request.content)

        run(split('cvlc file.wav'))
        return

async def player_turn(master_text, player : int):

    # It's assumed there will be always an .txt file named history.txt
    history = "" 

    with open("history.txt", 'r') as f:
        for line in f:
            print(line)
            history += f.readline()

    # Player's turn
    await player_complete_action
    async def player_complete_action(player_prompt : str, history : str):
        player_prompt = f"""{player_map[player]} 
        Descrição dos eventos ocorridos:
        {history}"""

        player_response = gemma_client.models.generate_content(
            model="gemma-3-27b-it",
            contents=player_prompt,
        )

        player_text = player_response.text
        print(player_text)

        # Done: put player speak here
        await player_speak(player, player_text)

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


def register_to_history():
    pass

if __name__ == '__main__':
    asyncio.run(main())

