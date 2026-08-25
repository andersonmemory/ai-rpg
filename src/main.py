import os
from utils import *


def main():

    ai = read_stream(
        "Você está em 1982, numa prisão. Na sua frente uma pequena serra caseira, na sua esquerda a porta da cela, e na sua direita uma janela com grades de ferro, o que você faz?"
    )
    while True:
        dm = input("\nDM: ")
        ai = read_stream(dm)


if __name__ == "__main__":
    main()
