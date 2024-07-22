import asyncio
import websockets

async def hello():
    uri = "ws://localhost:5679"
    async with websockets.connect(uri) as websocket:
        async for payload in websocket:
            _ = payload

try:
    asyncio.get_event_loop().run_until_complete(hello())
except Exception as e:
    import sys
    sys.exit(1)
