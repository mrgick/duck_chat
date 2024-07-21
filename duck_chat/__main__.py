import asyncio
import sys

from .cli import CLI


async def main():
    await CLI().run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
