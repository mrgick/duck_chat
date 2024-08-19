from types import TracebackType
from typing import AsyncGenerator, Self

import aiohttp
import msgspec
from fake_useragent import UserAgent

from .exceptions import (
    ConversationLimitException,
    DuckChatException,
    RatelimitException,
)
from .models import History, ModelType


class DuckChat:
    def __init__(
        self,
        model: ModelType = ModelType.Claude,
        session: aiohttp.ClientSession | None = None,
        user_agent: UserAgent | str = UserAgent(min_version=120.0),
    ) -> None:
        if type(user_agent) is str:
            self.user_agent = user_agent
        else:
            self.user_agent = user_agent.random

        self._session = session or aiohttp.ClientSession(
            headers={
                "Host": "duckduckgo.com",
                "Accept": "text/event-stream",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://duckduckgo.com/",
                "User-Agent": self.user_agent,
                "DNT": "1",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers",
            }
        )
        self.vqd: list[str | None] = []
        self.history = History(model, [])
        self.__encoder = msgspec.json.Encoder()
        self.__decoder = msgspec.json.Decoder()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await self._session.__aexit__(exc_type, exc_value, traceback)

    async def get_vqd(self) -> None:
        """Get new x-vqd-4 token"""
        async with self._session.get(
            "https://duckduckgo.com/duckchat/v1/status", headers={"x-vqd-accept": "1"}
        ) as response:
            if response.status == 429:
                res = await response.read()
                try:
                    err_message = self.__decoder.decode(res).get("type", "")
                except Exception:
                    raise DuckChatException(res.decode())
                else:
                    raise RatelimitException(err_message)
            self.vqd.append(response.headers.get("x-vqd-4"))
            if not self.vqd:
                raise DuckChatException("No x-vqd-4")

    async def get_answer(self) -> AsyncGenerator[str, None]:
        """Get message answer from chatbot"""
        async with self._session.post(
            "https://duckduckgo.com/duckchat/v1/chat",
            headers={
                "Content-Type": "application/json",
                "x-vqd-4": self.vqd[-1],
            },
            data=self.__encoder.encode(self.history),
        ) as response:
            if response.status == 429:
                raise RatelimitException(await response.text())
            try:
                async for line in response.content:
                    if line.startswith(b"data: "):
                        line = line[len("data: "):]
                        if line.startswith(b"[DONE]"):
                            break
                        try:
                            data = self.__decoder.decode(line)
                            if isinstance(data, list):
                                for message_part in data:
                                    yield message_part.get("message", "")
                            else:
                                yield data.get("message", "")
                        except Exception:
                            raise DuckChatException(f"Couldn't parse body={line.decode()}")
            except Exception as e:
                raise DuckChatException(f"Error while streaming data: {str(e)}")
        self.vqd.append(response.headers.get("x-vqd-4"))

    async def ask_question(self, query: str) -> str:
        """Get answer from chat AI"""
        if not self.vqd:
            await self.get_vqd()
        self.history.add_input(query)

        full_message = []
        async for part in self.get_answer():
            print(part, end='', flush=True)
            full_message.append(part)

        full_message_str = "".join(full_message)
        self.history.add_answer(full_message_str)
        return full_message_str
