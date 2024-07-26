if __name__ == "__main__":
    import asyncio

    from .cli import CLI

    asyncio.run(CLI().run())
