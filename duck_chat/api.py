from types import TracebackType
from typing import AsyncGenerator, Self

import asyncio
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
        proxy: str | None = None,
        max_retries: int = 3, 
        delay: int = 10, 
    ) -> None:
        """Initialize the DuckChat instance.

        Args:
            model: The model type to use (default: ModelType.Claude).
            session: An optional aiohttp.ClientSession. If not provided, a new session is created.
            user_agent: A UserAgent object or string for the HTTP User-Agent header.
            proxy: An optional proxy URL (e.g., "http://proxy.example.com:8080") to use for requests.
            max_retries: Maximum number of retry attempts for rate limit errors (default: 3).
            delay: Delay in seconds between retry attempts (default: 10).
        """
        if isinstance(user_agent, str):
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
                "x-vqd-4": "",
                "DNT": "1",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers",
            }
        )
        self.vqd: list[str] = []
        self.history = History(model, [])
        self.__encoder = msgspec.json.Encoder()
        self.__decoder = msgspec.json.Decoder()
        self.proxy = proxy
        self.max_retries = max_retries  # Store as class property
        self.delay = delay  # Store as class property

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await self._session.__aexit__(exc_type, exc_value, traceback)

    async def get_answer(self) -> str:
        """Get message answer from chatbot with retry logic for rate limits"""
        attempt = 0  # Local variable for attempt counter
        while attempt < self.max_retries:
            async with self._session.post(
                "https://duckduckgo.com/duckchat/v1/chat",
                headers={
                    "Content-Type": "application/json",
                    "x-vqd-4": self.vqd[-1],
                },
                data=self.__encoder.encode(self.history),
            ) as response:
                res = await response.read()
                if response.status == 429:
                    raise RatelimitException(res.decode())
                try:
                    data = self.__decoder.decode(
                        b"["
                        + b",".join(
                            res.lstrip(b"data: ").rstrip(b"\n\ndata: [DONE][LIMIT_CONVERSATION]\n").split(b"\n\ndata: ")
                        )
                        + b"]"
                    )
                except Exception:
                    raise DuckChatException(f"Couldn't parse body={res.decode()}")
                message = []
                has_error = False
                for x in data:
                    if x.get("action") == "error":
                        err_message = x.get("type", "") or str(x)
                        if err_message == "ERR_BN_LIMIT":
                            has_error = True
                            break
                        elif x.get("status") == 429:
                            if err_message == "ERR_CONVERSATION_LIMIT":
                                raise ConversationLimitException(err_message)
                            raise RatelimitException(err_message)
                        else:
                            raise DuckChatException(err_message)
                    message.append(x.get("message", ""))
                if not has_error:
                    self.vqd.append(response.headers.get("x-vqd-4", ""))
                    return "".join(message)
                attempt += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.delay)
        raise DuckChatException(f"ERR_BN_LIMIT after {self.max_retries} attempts")

    async def get_vqd(self) -> None:
        """Get new x-vqd-4 token."""
        async with self._session.get(
            "https://duckduckgo.com/duckchat/v1/status",
            headers={"x-vqd-accept": "1"},
            proxy=self.proxy,
        ) as response:
            if response.status == 429:
                res = await response.read()
                try:
                    err_message = self.__decoder.decode(res).get("type", "")
                except Exception:
                    raise DuckChatException(res.decode())
                else:
                    raise RatelimitException(err_message)
            if "x-vqd-4" in response.headers:
                self.vqd.append(response.headers["x-vqd-4"])
            else:
                raise DuckChatException("No x-vqd-4")

    async def stream_answer(self) -> AsyncGenerator[str, None]:
        """Stream answer from chatbot."""
        async with self._session.post(
            "https://duckduckgo.com/duckchat/v1/chat",
            headers={
                "Content-Type": "application/json",
                "x-vqd-4": self.vqd[-1],
            },
            data=self.__encoder.encode(self.history),
            proxy=self.proxy,
        ) as response:
            if response.status == 429:
                raise RatelimitException(await response.text())
            try:
                async for line in response.content:
                    if line.startswith(b"data: "):
                        chunk = line[6:]
                        if chunk.startswith(b"[DONE]"):
                            break
                        try:
                            data = self.__decoder.decode(chunk)
                            if "message" in data and data["message"]:
                                yield data["message"]
                        except Exception:
                            raise DuckChatException(f"Couldn't parse body={chunk.decode()}")
            except Exception as e:
                raise DuckChatException(f"Error while streaming data: {str(e)}")
        self.vqd.append(response.headers.get("x-vqd-4", ""))

    async def ask_question(self, query: str) -> str:
        """Get answer from chat AI."""
        if not self.vqd:
            await self.get_vqd()
        self.history.add_input(query)
        message = await self.get_answer()
        self.history.add_answer(message)
        return message

    async def reask_question(self, num: int) -> str:
        """Get re-answer from chat AI."""
        if num >= len(self.vqd):
            num = len(self.vqd) - 1
        self.vqd = self.vqd[:num]
        if not self.history.messages:
            return ""
        if not self.vqd:
            await self.get_vqd()
            self.history.messages = [self.history.messages[0]]
        else:
            num = min(num, len(self.vqd))
            self.history.messages = self.history.messages[: (num * 2 - 1)]
        message = await self.get_answer()
        self.history.add_answer(message)
        return message

    async def ask_question_stream(self, query: str) -> AsyncGenerator[str, None]:
        """Stream answer from chat AI."""
        if not self.vqd:
            await self.get_vqd()
        self.history.add_input(query)
        message_list = []
        async for message in self.stream_answer():
            yield message
            message_list.append(message)
        self.history.add_answer("".join(message_list))

    async def reask_question_stream(self, num: int) -> AsyncGenerator[str, None]:
        """Stream re-answer from chat AI."""
        if num >= len(self.vqd):
            num = len(self.vqd) - 1
        self.vqd = self.vqd[:num]
        if not self.history.messages:
            raise GeneratorExit("There is no history messages")
        if not self.vqd:
            await self.get_vqd()
            self.history.messages = [self.history.messages[0]]
        else:
            num = min(num, len(self.vqd))
            self.history.messages = self.history.messages[: (num * 2 - 1)]
        message_list = []
        async for message in self.stream_answer():
            yield message
            message_list.append(message)
        self.history.add_answer("".join(message_list))