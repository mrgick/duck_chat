import json
from typing import Dict, Any
import httpx
from config import settings


def get_headers() -> Dict[str, str]:
    return {
        "Host": "duckduckgo.com",
        "Accept": "text/event-stream",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://duckduckgo.com/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Cookie": "dcm=3; ay=b",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }


async def simulate_browser_reqs(client: httpx.Client):
    headers = get_headers()
    headers["X-Requested-With"] = "XMLHttpRequest"
    r = await client.get("https://duckduckgo.com/country.json", headers=headers)
    # print(r.text)


async def get_vqd(client: httpx.Client) -> str:
    headers = get_headers()
    headers["Cache-Control"] = "no-store"
    headers["x-vqd-accept"] = "1"
    response = await client.get(
        "https://duckduckgo.com/duckchat/v1/status", headers=headers
    )
    vqd = response.headers.get("x-vqd-4")
    if vqd:
        # print(vqd)
        return vqd
    else:
        raise Exception("No VQD header returned")


async def get_res(client: httpx.Client, query: str, vqd: str):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "x-vqd-4": vqd,
    }

    message = []
    print(settings.model.value)
    async with client.stream(
        "POST",
        "https://duckduckgo.com/duckchat/v1/chat",
        headers=headers,
        json={
            "model": settings.model.value,
            "messages": [{"role": "user", "content": query}],
        },
    ) as response:
        async for chunk in response.aiter_lines():
            z = chunk.replace("data: ", "").replace("\n", "").strip()
            if not z or z == "[DONE]":
                continue
            try:
                obj = json.loads(z)
                if type(obj) is dict and obj.get("message"):
                    message.append(obj["message"])
            except:
                print(z)
        new_vqd = response.headers.get("x-vqd-4")
    if not new_vqd:
        print(
            "Warn: DuckDuckGo did not return new VQD. Ignore this if everything else is ok."
        )
    return "".join(message), new_vqd
