from enum import Enum

import msgspec

from .model_type import ModelType


class Role(Enum):
    user = "user"
    assistant = "assistant"


class Message(msgspec.Struct):
    role: Role
    content: str


class History(msgspec.Struct):
    model: ModelType
    messages: list[Message]

    def add_input(self, message: str) -> None:
        self.messages.append(Message(Role.user, message))

    def add_answer(self, message: str) -> None:
        self.messages.append(Message(Role.assistant, message))
