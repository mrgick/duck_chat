import tomllib
from pathlib import Path

from ..models import ModelType


class Settings:
    def __init__(self) -> None:
        self.model = self.read_model_from_conf()
        self.INPUT_MODE = "singleline"
        self.STREAM_MODE = False
        self.COUNT = 1

    def read_model_from_conf(self) -> ModelType:
        filepath = Path.home() / ".config" / "hey" / "conf.toml"
        if filepath.exists():
            with open(filepath, "rb") as f:
                conf = tomllib.load(f)
                model_name = conf["model"]
            if model_name in (x.name for x in ModelType):
                if model_name == "GPT3":
                    print("\033[1;1m GPT3 is deprecated! Use GPT4o\033[0m")
                return ModelType[model_name]
        return ModelType.Claude
