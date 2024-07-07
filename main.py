from api import DuckChat
from config import ModelType
import asyncio


async def main():
    async with DuckChat(model=ModelType.GPT3) as chat:
        print(await chat.get_res("2+2?"))


asyncio.run(main())
