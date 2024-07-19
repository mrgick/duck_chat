import asyncio
import sys

from .api import DuckChat
from .config import ModelType


async def main():
    async with DuckChat(model=ModelType.read_model_from_conf()) as chat:
        print('Type \033[1;4mstop\033[0m to quit')
        while True:
            try:
                print("\033[1;4m>>> User input:\033[0m", end="\n")
                question = input()
            except EOFError:
                sys.exit(0)
            if question == "stop":
                break
            print("\033[1;4m>>> Response:\033[0m", end="\n")
            print(await chat.ask_question(question))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
