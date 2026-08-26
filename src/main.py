import os
import random
from utils import *


instructions_A = """
Português do Brasil.
Você é Jorge, um mecânico silencioso que prioriza lógica, ferramentas e soluções práticas para resolver qualquer problema sem chamar atenção.
### Máximo de 1 frase em 1ª pessoa. Apenas declare o que você tenta fazer de forma fria e calculada, sem narrar o resultado da ação.
"""

instructions_B = """
Português do Brasil.
Você é Beto, um jovem impulsivo e barulhento que odeia planejar e tenta resolver tudo na base da pressa, força bruta ou confronto direto.
### Máximo de 1 frase em 1ª pessoa. Apenas declare sua ação precipitada e fale em tom urgente, sem narrar o resultado da ação.
"""

instructions_C = """
Português do Brasil.
Você é Clara, uma estelionatária astuta que evita qualquer esforço físico e prefere usar lábia, blefes e manipulação psicológica para conseguir o que quer.
### Máximo de 1 frase em 1ª pessoa. Apenas declare sua tentativa de persuasão ou observação de forma calma e irônica, sem narrar o resultado da ação.
"""

players = []


def dm(content: str):

    global_messages.append({"role": "user", "content": f"[DM]: {content}"})


def say(player: Player):

    name = player.name
    content = player.answer()


def main():

    agent_A = Player("Jorge", instructions_A)
    agent_B = Player("Beto", instructions_B)
    agent_C = Player("Clara", instructions_C)

    players.extend([agent_A, agent_B, agent_C])

    identifiers = {"1": agent_A, "2": agent_B, "3": agent_C}

    dm(
        "Vocês três estão em 1982, numa prisão, Jorge, Beto e Clara. Na sua frente uma pequena serra caseira, na sua esquerda a porta da cela, e na sua direita uma janela com grades de ferro, o que você faz?"
    )

    for player in players:
        say(player)

    while True:
        if len(global_messages) >= MAX_MESSAGES:
            summarize()
            continue

        dm_answer = input("\nDM: ")

        match dm_answer:
            case "d6":
                print(d6())
                continue
            case "2d6":
                print([d6(), d6()])
                continue

        if dm_answer in ["1", "2", "3"]:
            answer = input(f"Dizer para {identifiers[dm_answer].name}: ")
            dm(f"[DM -> dizendo para {identifiers[dm_answer].name}]: {answer}")
            say(identifiers[dm_answer])
            continue

        if dm_answer != "":
            dm(f"[DM]: {dm_answer}")

        random.shuffle(players)

        for player in players:
            say(player)


def d6():
    return random.randint(1, 6)


if __name__ == "__main__":
    main()
