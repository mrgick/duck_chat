import argparse
import asyncio

from ..models.generate_models import main as generator
from .cli import CLI
from .config import Settings


def safe_entry_point() -> None:
    parser = argparse.ArgumentParser(description="Duck chat CLI")
    parser.add_argument("--generate", action="store_true", help="Generate new models")
    parser.add_argument("--config", action="store_true", help="Set config")
    args = parser.parse_args()
    if args.generate:
        generator()
    if args.config:
        Settings.set_settings()
    else:
        asyncio.run(CLI().run())
