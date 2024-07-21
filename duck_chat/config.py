from enum import Enum
from pathlib import Path

import tomllib


class ModelType(Enum):
    Claude = "claude-3-haiku-20240307"
    GPT3 = "gpt-3.5-turbo-0125"
    Llama = "meta-llama/Llama-3-70b-chat-hf"
    Mixtral = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    def read_model_from_conf():
        filepath = Path.home() / ".config" / "hey" / "conf.toml"
        if filepath.exists():
            with open(filepath, "rb") as f:
                conf = tomllib.load(f)
                model_name = conf["model"]
            if ModelType[model_name]:
                return ModelType[model_name]
        return ModelType.Claude
