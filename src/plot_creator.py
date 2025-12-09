# This file is going to create the plot 
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

start_time = None


# game_system = None
player_creator = None
game_introduction = None

def main():

    # if not len(sys.argv) == 2:
    #     print("Usage: python player_creator.py <output.txt>")
    #     sys.exit()

    # output_filename = sys.argv[1]

    global start_time

    plot_info = None

    with open("settings/plot_info.txt", 'r') as f:
        plot_info = f.read()

    # Ask for the die values for the plot
    first = int(input("Algo aconteceu: "))
    second = int(input("Você precisa: "))
    third = int(input("Senão: "))    

    first = plot(first, "algo aconteceu", plot_info)
    second = plot(second,"você precisa", plot_info)
    third = plot(third, "senão", plot_info)

    print(first + second + third)

    player1 = input("Arquivo do jogador1: ")
    player2 = input("Arquivo do jogador2: ")

    p1_path = Path.cwd() / "characters" / f"{player1}"
    p2_path = Path.cwd() / "characters" / f"{player2}"

    if not os.path.exists(p1_path) or not os.path.exists(p2_path):
        print("Arquivo não encontrado para um dos jogadores.")
        sys.exit()

    with open(f"{p1_path}", 'r') as f:
        player1 = f.read()

    with open(f"{p2_path}", 'r') as f:
        player2 = f.read()
    
    player1_summary = player_summarizer(player1)
    player2_summary = player_summarizer(player2)

    print(player1_summary)
    print(player2_summary)

    world_explanation = input("Descreva a trama, objetivo e como os jogadores se encontraram: ")

    start_time = time.perf_counter()

    # 1, 6, 3
    # Alves e Almeida se encontraram depois do trabalho, para a investigação de um sumiço desconhecido, não se sabe exatamente o motivo. 
    # Eles sentem que precisam encontrar alguém, que deve saber o que está por trás disso, senão a verdade será esquecida.

    # prompt = player_creator + basic_description + initiative_text + game_introduction 

    # Insert the prompt to the AI
    # response = client.models.generate_content(model="gemma-3-27b-it", contents=prompt)

    # with open(f"characters/{output_filename}", 'w') as f:
        # f.write(response.text)


# logic for the plot creation
def plot(die, type : str, plot : str):

    topic = None

    valid_types = ["algo aconteceu", "você precisa", "senão"]

    if type in valid_types:
        topic = type
    else:
        print("Wrong event name.") 
        sys.exit()        

    prompt = f"""

    ### Instrução ### 
    SISTEMA: Você está escolhendo qual opção é a adequada para os valores que lhe foram fornecidos.

    Uma lista de três tópicos foi fornecida, cada uma contendo seis valores. 
    
    Com base na seção "valor escolhido", pegue o valor que possui exata enumeração e está dentro do exato tópico
    que foi fornecido. A comparação é feita contra a seção "Lista" que possui os três tópicos com os seis valores.

    Sua resposta deve sempre seguir o formato da seção "formato".
    
    ### Formato ###
    <nome_do_valor>

    ### Valor escolhido: ###
        Tópico: {topic}
        Enumeração: {die}


    ### Lista ###
    {plot}
    """
    
    response = client.models.generate_content(model="gemma-3-27b-it", contents=prompt)

    with open("data/plot.txt", 'w') as f:
        f.write(response.text) 
    
    return f"{topic}: {response.text}"
    

def player_summarizer(player_info):

    summary = f"""
        ### Instrução ###
        SISTEMA: você está resumindo o texto.

        Deve explicar em 1-2 sentenças a visão geral da descrição de um jogador que lhe foi dada.

        ### Descrição ###

        {player_info}
    """

    response = client.models.generate_content(model="gemma-3-27b-it", contents=summary)

    return response.text

def world_explainer():

    pass

# you_need = int(input("Você precisa: "))
# otherwise = int(input("Senão: "))    



if __name__ == '__main__':

    with open("settings/player_creator_prompt.txt", 'r') as f:
        player_creator = f.read() 

    with open("settings/game_introduction.txt", 'r') as f:
       game_introduction = f.read() 

    main()
    end_time = time.perf_counter()
    time_elapsed = end_time - start_time
    print(f"✅ Success. \n⏱️ Time taken: {time_elapsed:.06f}") 