import asyncio
from google import genai
from google.genai import types

async def test():
    client = genai.Client(api_key="TEST")
    print(dir(client.aio.models))

asyncio.run(test())
