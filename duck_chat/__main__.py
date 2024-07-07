import asyncio
import sys

from .api import DuckChat
from .config import ModelType


async def main():
    async with DuckChat(model=ModelType.Claude) as chat:
        while True:
            try:
                question = input()
            except EOFError:
                sys.exit(0)
            if question == "stop":
                break
            print(await chat.ask_question(question))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
