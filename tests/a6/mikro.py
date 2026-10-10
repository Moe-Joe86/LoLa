"""A6: schaltet das Mikrofon der App stumm oder wieder an (damit Patrick diktieren kann, ohne dass LoLa mithört).

Aufruf (Umgebung mit `websockets`): python tests/a6/mikro.py stumm | an
"""

import asyncio
import json
import sys

import websockets


async def main(stumm: bool) -> None:
    async with websockets.connect("ws://127.0.0.1:7860/rpc", max_size=None) as ws:
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "conversation.mic", "params": {"muted": stumm}}))
        while json.loads(await asyncio.wait_for(ws.recv(), 10)).get("id") != 1:
            pass
    print("Mikrofon", "stumm" if stumm else "an")


asyncio.run(main(sys.argv[1] == "stumm"))
