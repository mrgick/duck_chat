from api import simulate_browser_reqs, get_vqd, get_res
import asyncio
import httpx
from config import settings, ModelType


async def main():
    settings.model = ModelType.Claude
    client = httpx.AsyncClient()
    await simulate_browser_reqs(client)
    vqd = await get_vqd(client)
    mes, vqd = await get_res(client, "Who are you?", vqd)
    print(mes, vqd)
    await asyncio.sleep(0.1)
    mes, vqd = await get_res(client, "How are you?", await get_vqd(client))
    print(mes, vqd)
    await client.aclose()


asyncio.run(main())
