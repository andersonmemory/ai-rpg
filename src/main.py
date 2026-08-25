import os
from utils import *
import random


instructions_A = """
Você é Jorge, um mecânico silencioso que prioriza lógica, ferramentas e soluções práticas para resolver qualquer problema sem chamar atenção.

Máximo de 2 frases em 1ª pessoa. Apenas declare o que você tenta fazer de forma fria e calculada, sem narrar o resultado da ação.
"""

instructions_B = """
Você é Beto, um jovem impulsivo e barulhento que odeia planejar e tenta resolver tudo na base da pressa, força bruta ou confronto direto.

Máximo de 2 frases em 1ª pessoa. Apenas declare sua ação precipitada e fale em tom urgente, sem narrar o resultado da ação.
"""

instructions_C = """
Você é Clara, uma estelionatária astuta que evita qualquer esforço físico e prefere usar lábia, blefes e manipulação psicológica para conseguir o que quer.

Máximo de 2 frases em 1ª pessoa. Apenas declare sua tentativa de persuasão ou observação de forma calma e irônica, sem narrar o resultado da ação.
"""

players = []


def dm(content: str):

    for player in players:
        player.add_to_memory({"role": "user", "content": content})


def say(player: Player):

    name = player.name
    content = player.answer()

    for player in players:
        if player.name == name:
            continue

        player.add_to_memory(
            {"role": "user", "content": f"{name} disse/decidiu fazer: {content}"}
        )


def main():

    agent_A = Player("Jorge", instructions_A)
    agent_B = Player("Beto", instructions_B)
    agent_C = Player("Clara", instructions_C)

    players.extend([agent_A, agent_B, agent_C])

    dm(
        "DM: Vocês três estão em 1982, numa prisão, Jorge, Beto e Clara. Na sua frente uma pequena serra caseira, na sua esquerda a porta da cela, e na sua direita uma janela com grades de ferro, o que você faz?"
    )

    for player in players:
        say(player)

    # print("==============")
    # print(agent_A.messages)
    # print("==============")
    # print(agent_B.messages)
    # print("==============")
    # print(agent_C.messages)
    # print("==============")
    #
    # agent_C.answer(f"")

    while True:
        dm(input("\nDM: "))

        # ai = vanderlei.answer(dm)


if __name__ == "__main__":
    main()
