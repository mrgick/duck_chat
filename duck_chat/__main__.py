import asyncio

from .api import DuckChat
from .config import ModelType


async def main():
    async with DuckChat(model=ModelType.Claude) as chat:
        while True:
            question = input()
            if question == "stop":
                break
            print(await chat.ask_question(question))


asyncio.run(main())
