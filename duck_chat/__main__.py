import asyncio
import sys

from .cli import run


async def main():
    await run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
