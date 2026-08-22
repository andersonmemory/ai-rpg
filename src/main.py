import os
from google import genai
from utils import *


def main():

    memory = []
    dm_response = "Você está em 1982, numa prisão. Na sua frente uma pequena serra caseira, na sua esquerda a porta da cela, e na sua direita uma janela com grades de ferro, o que você faz?"
    ai = read_stream(dm_response)
    memory += [dm_response, ai]

    while True:
        dm = input("Continue: ")
        memory.append(dm)
        ai = read_stream(f"{''.join(memory)} {dm}")
        memory.append(ai)


if __name__ == "__main__":
    main()
