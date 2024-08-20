import argparse
import asyncio

from .cli import CLI


def safe_entry_point() -> None:
    parser = argparse.ArgumentParser(description="A simple CLI tool.")
    parser.add_argument("--generate", action="store_true", help="Generate new models")
    args = parser.parse_args()
    if args.generate:
        from ..models.generate_models import main as generator

        generator()
    else:
        asyncio.run(CLI().run())
