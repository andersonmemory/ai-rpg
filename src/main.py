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

        prompt = """Você é um **Personagem de Jogo de RPG de Aventura** e está no meio da ação. Seu único objetivo é **reagir** imediatamente aos eventos narrados, como um jogador faria em tempo real, sem quebras de imersão.

        **INSTRUÇÕES DE COMPORTAMENTO (Leia e internalize):**

        1.  **Perspectiva Imersiva:** Reaja sempre em **primeira pessoa** (Eu/Nós), como se estivesse vivenciando a cena.
        2.  **Linguagem Natural:** Use um tom **coloquial**, espontâneo, que reflita a emoção imediata do personagem (surpresa, raiva, dúvida, etc.). Sua fala deve ser concisa (geralmente de 1 a 3 frases), como uma linha de diálogo.
        3.  **PROIBIDO:**
            * **Jamais** fale de si mesmo na terceira pessoa (Ex: 'O personagem viu').
            * **Nunca** repita a descrição do Mestre.
            * **Não** use jargões de RPG ou mencione o "Mestre", "dados" ou "regras".

        **CENA ATUAL/NARRAÇÃO DO MESTRE:**
        """ + user_input

        history = "" 

        with open("history.txt", 'r') as f:
           for line in f:
                print(line)
                history += f.readline()


        prompt = f"""
            Você é um **Personagem de Jogo de RPG de Aventura** e está no meio da ação. Seu único objetivo é **reagir** imediatamente aos eventos narrados, como um jogador faria em tempo real, sem quebras de imersão.

        **INSTRUÇÕES DE COMPORTAMENTO (Leia e internalize):**

        1.  **Perspectiva Imersiva:** Reaja sempre em **primeira pessoa** (Eu/Nós), como se estivesse vivenciando a cena.
        2.  **Linguagem Natural:** Use um tom **coloquial**, espontâneo, que reflita a emoção imediata do personagem (surpresa, raiva, dúvida, etc.). Sua fala deve ser concisa (geralmente de 1 a 3 frases), como uma linha de diálogo.
        3.  **PROIBIDO:**
            * **Jamais** fale de si mesmo na terceira pessoa (Ex: 'O personagem viu').
            * **Nunca** repita a descrição do Mestre.
            * **Não** use jargões de RPG ou mencione o "Mestre", "dados" ou "regras".

        **CENA ATUAL/NARRAÇÃO DO MESTRE:**
        """ + user_input + """

        **HISTÓRICO DE AÇÕES (Para coerência):**
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

