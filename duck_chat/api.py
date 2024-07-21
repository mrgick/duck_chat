from http import HTTPStatus
from types import TracebackType
from typing import Self

import msgspec
from curl_cffi.requests import AsyncSession

from .config import ModelType


class DuckChat:
    def __init__(
        self,
        model: ModelType = ModelType.Claude,
        client: AsyncSession = AsyncSession(impersonate="chrome124"),
    ) -> None:
        self._client = client
        self._model = model
        self._vqd = None
        self._history = []

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await self._client.__aexit__(exc_type, exc_value, traceback)

    def get_headers(self):
        return {
            # "Host": "duckduckgo.com",
            # "Accept": "text/event-stream",
            # "Accept-Language": "en-US,en;q=0.5",
            # "Accept-Encoding": "gzip, deflate, br",
            # "Referer": "https://duckduckgo.com/",
            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
            # "DNT": "1",
            # "Sec-GPC": "1",
            # "Connection": "keep-alive",
            # "Sec-Fetch-Dest": "empty",
            # "Sec-Fetch-Mode": "cors",
            # "Sec-Fetch-Site": "same-origin",
            # "TE": "trailers",
        }

    async def simulate_browser_reqs(self) -> None:
        response = await self._client.get(
            "https://duckduckgo.com/country.json",
            headers={
                **self.get_headers(),
                **{"X-Requested-With": "XMLHttpRequest"},
            },
        )
        if response.status_code != HTTPStatus.OK:
            print("Can't get country json (maybe ip ban)")

    async def get_vqd(self, first: bool) -> None:
        headers = self.get_headers()
        headers["Cache-Control"] = "no-store"
        if first:
            headers["x-vqd-accept"] = "1"
        response = await self._client.get(
            "https://duckduckgo.com/duckchat/v1/status", headers=headers
        )
        vqd = response.headers.get("x-vqd-4")
        if vqd:
            self._vqd = vqd

    async def get_res(self) -> str:
        message = []
        response = await self._client.post(
            "https://duckduckgo.com/duckchat/v1/chat",
            headers={
                "Content-Type": "application/json",
                "x-vqd-4": self._vqd,
            },
            data=msgspec.json.encode(
                {
                    "model": self._model.value,
                    "messages": self._history,
                }
            ),
            stream=True,
        )
        message = ""
        async for chunk in response.aiter_content():
            try:
                for x in chunk.split(b"data: "):
                    x = x[:-2]
                    if not x or x == b"[DONE]":
                        continue
                    v = msgspec.json.decode(x)["message"]
                    message += v
                    yield v
            except Exception:
                print(f"Unparsed chunk: {chunk}")
        new_vqd = response.headers.get("x-vqd-4")
        if new_vqd:
            self._vqd = new_vqd
        self._history.append({"role": "assistant", "content": message})
        # return "".join(message)

    async def ask_question(self, query: str) -> str:
        # try:
        if not self._history:
            await self.simulate_browser_reqs()
            await self.get_vqd(first=True)
        else:
            await self.get_vqd(first=False)
        self._history.append({"role": "user", "content": query})
        async for x in self.get_res():
            yield x

        # return result
        # except Exception as e:
        #     print(e)
        #     return ""
