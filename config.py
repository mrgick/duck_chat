from dataclasses import dataclass
from enum import Enum, auto


class ModelType(Enum):
    Claude = "claude-3-haiku-20240307"
    GPT3 = "gpt-3.5-turbo-0125"
    Llama = "meta-llama/Llama-3-70b-chat-hf"
    Mixtral = "mistralai/Mixtral-8x7B-Instruct-v0.1"


@dataclass
class Settings:
    model: ModelType = ModelType.Claude


settings = Settings()
