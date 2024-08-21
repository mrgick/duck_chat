from pathlib import Path
from typing import Literal

import msgspec
from platformdirs import user_config_dir
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

from ..models import ModelType


class Settings(msgspec.Struct, rename="kebab"):
    MODEL: Literal[*[x.name for x in ModelType]] = list(ModelType)[0].name  # type: ignore
    INPUT_MODE: Literal["singleline", "multiline"] = "singleline"
    STREAM_MODE: bool = False

    @classmethod
    def load_settings(cls) -> "Settings":
        config_path: Path = Path(user_config_dir("duck_chat")) / "conf.toml"
        if not config_path.exists():
            settings = Settings()
            cls.write_settings(settings)
            return settings
        with open(config_path, "rb") as f:
            buff = f.read()
        try:
            settings = msgspec.toml.decode(buff, type=Settings, strict=False)
        except msgspec.ValidationError as e:
            print("Validation error occurred while loading conf.toml:")
            print(f"Field: {e}")
            quit()
        return settings

    @classmethod
    def write_settings(cls, settings: "Settings") -> None:
        config_path: Path = Path(user_config_dir("duck_chat")) / "conf.toml"
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "wb") as f:
            f.write(msgspec.toml.encode(settings))
        console = Console()
        text = Text(f"Wrote settings to {config_path.absolute()}")
        text.stylize("bold magenta", 18)
        console.print(text)

    @classmethod
    def set_settings(cls) -> None:
        settings = Settings()
        settings.MODEL = Prompt.ask("Choose model", choices=[x.name for x in ModelType], default=settings.MODEL)
        settings.INPUT_MODE = Prompt.ask(
            "Choose input mode", choices=["singleline", "multiline"], default=settings.INPUT_MODE
        )  # type: ignore
        settings.STREAM_MODE = bool(
            Prompt.ask("Stream mode on?", choices=["True", "False"], default=str(settings.STREAM_MODE))
        )
        cls.write_settings(settings)
