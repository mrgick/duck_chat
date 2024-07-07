from api import DuckChat
from config import ModelType
import asyncio


async def main():
    async with DuckChat(model=ModelType.GPT3) as chat:
        while True:
            question = input()
            if question == "stop":
                break
            print(await chat.ask_question(question))


asyncio.run(main())
