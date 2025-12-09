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


player_creator = None
game_introduction = None

def main():

    global start_time

    plot_info = None

    with open("settings/plot_info.txt", 'r') as f:
        plot_info = f.read()

    # Ask for the die values for the plot
    first = int(input("Algo aconteceu: "))
    second = int(input("Você precisa: "))
    third = int(input("Senão: "))    

    # Grab part of the plot info based on the dice's values.
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

    print(f"{player1_summary}\n")
    print(player2_summary)

    world_explanation = input("Descreva a trama, objetivo e como os jogadores se encontraram: ")

    start_time = time.perf_counter()

    raw_plot = first + second + third

    world_explanation = world_plot_explainer(world_explanation, player1_summary, player2_summary, raw_plot)

    how_to_play = None

    with open("settings/how_to_play_prompt.txt", 'r') as f:
        how_to_play = f.read()
 

    how_to_play = how_to_play + world_explanation

    final_file = how_to_play

    print(final_file)

    with open("data/plot.txt", 'w') as f:
        f.write(final_file)


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

def world_plot_explainer(explanation : str, player1_summary : str, player2_summary : str, raw_plot : str):

    prompt = f"""


    ### Instrução ###

    SISTEMA: você está definindo uma trama principal de um jogo RPG.

    Reescreva os dados fornecidos na seção "dados" para que a mensagem da trama 
    fique mais clara e coerente. Evite mudar informações como nomes de pessoas,
    quem procurar ou eventos a se fazer.

    Você vai escrever no formato apresentado na seção "formato" 

    Uma leve explicação de cada jogador está presente, para ser enriquecer o texto
    que resume a trama principal. A explicação está na seção "jogadores"

    Note que, somente a informação da trama deve ser posta, evitando qualquer tipo
    de outra formatação como <>, ### ou até mesmo títulos.

    Na seção "Plot original" é a base e o esqueleto da trama inteira. Por isso,
    é de extrema importância que seja adaptado no texto final.

    ### Jogadores ###

    {player1_summary}

    {player2_summary}

    ### Plot original ###

    Plot original: 
    
    {raw_plot}


    ### Formato ###
    <informação-sobre-a-trama>


    ### Dados ####

    {explanation}
    """

    response = client.models.generate_content(model="gemma-3-27b-it", contents=prompt)

    return response.text


if __name__ == '__main__':

    with open("settings/player_creator_prompt.txt", 'r') as f:
        player_creator = f.read() 

    with open("settings/game_introduction.txt", 'r') as f:
       game_introduction = f.read() 

    main()
    end_time = time.perf_counter()
    time_elapsed = end_time - start_time
    print(f"✅ Success. \n⏱️ Time taken: {time_elapsed:.06f}") 