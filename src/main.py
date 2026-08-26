import os
import random
from utils import *


players = []


def dm(content: str):

    global_messages.append({"role": "user", "content": f"[DM]: {content}"})


def say(player: Player):

    name = player.name
    content = player.answer()


def main():

    first_prompt = input("DM (prompt inicial): ")

    players.extend(generate_character(first_prompt))

    identifiers = {str(i + 1): players[i] for i in range(len(players))}

    dm(first_prompt)

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

        if dm_answer in ["1", "2", "3"] and len(dm_answer) == 1:
            answer = input(f"Dizer para {identifiers[dm_answer].name}: ")
            dm(f"[DM -> dizendo para {identifiers[dm_answer].name}]: {answer}")
            say(identifiers[dm_answer])
            continue
        elif len(dm_answer) == 2:
            if dm_answer[0].isdigit() and dm_answer[1].isdigit():
                first = identifiers[dm_answer[0]]
                second = identifiers[dm_answer[1]]
                answer = input(f"Dizer para {first.name} e {second.name}: ")
                dm(
                    f"[DM -> dizendo apenas para {first.name} e {second.name}]: {answer}"
                )
                say(first)
                say(second)
                continue

        if dm_answer != "":
            dm(dm_answer)

        random.shuffle(players)

        for player in players:
            say(player)


def d6():
    return random.randint(1, 6)


if __name__ == "__main__":
    main()
