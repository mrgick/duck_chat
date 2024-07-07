from api import DuckChat
from config import ModelType
import asyncio


async def main():
    async with DuckChat(model=ModelType.GPT3) as chat:
        print(await chat.ask_question("2+2?"))
        print(await chat.ask_question("Are you right?"))
        print(await chat.ask_question("Thank you, have a good day)"))


asyncio.run(main())
