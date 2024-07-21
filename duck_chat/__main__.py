import asyncio

from .cli import CLI


async def main():
    await CLI().run()


if __name__ == "__main__":
    asyncio.run(main())
