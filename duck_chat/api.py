from types import TracebackType
from typing import Self

import aiohttp
import msgspec

from .models import History, ModelType


class DuckChat:
    def __init__(
        self,
        model: ModelType = ModelType.Claude,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._session = session or aiohttp.ClientSession(
            headers={
                "Host": "duckduckgo.com",
                "Accept": "text/event-stream",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://duckduckgo.com/",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
                "DNT": "1",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers",
            }
        )
        self.vqd = None
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

    async def get_vqd(self, first: bool) -> None:
        """Get new x-vqd-4 token"""
        headers = {"x-vqd-accept": "1"} if first else {}
        async with self._session.get(
            "https://duckduckgo.com/duckchat/v1/status", headers=headers
        ) as response:
            self.vqd = response.headers.get("x-vqd-4") or self.vqd

    async def get_answer(self) -> str:
        """Get message answer from chatbot"""
        message = ""
        async with self._session.post(
            "https://duckduckgo.com/duckchat/v1/chat",
            headers={
                "Content-Type": "application/json",
                "x-vqd-4": self.vqd,
            },
            data=self.__encoder.encode(self.history),
        ) as response:
            message = "".join(
                x["message"]
                for x in self.__decoder.decode(
                    b"["
                    + (await response.read()).replace(b"\n\ndata: ", b",")[6:-9]
                    + b"]"
                )
            )
        self.vqd = response.headers.get("x-vqd-4") or self.vqd
        return message

    async def ask_question(self, query: str) -> str:
        """Get answer from chat AI"""
        if not self.vqd:
            await self.get_vqd(first=True)

        self.history.add_input(query)

        # double try to get answer
        message = await self.get_answer()

        self.history.add_answer(message)
        return message
