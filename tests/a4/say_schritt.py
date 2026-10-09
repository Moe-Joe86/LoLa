"""Schleust einen Satz über conversation.say ein. Das Mikrofon ist beim Senden kurz stumm (Vorschlag aus A7,
damit der Satz nicht verloren geht).

Aufruf (Umgebung mit `websockets`): python tests/a4/say_schritt.py <Nummer aus say_saetze.txt | "freier Text">
"""

import asyncio
import json
import sys
import time
from pathlib import Path

import websockets

ADRESSE = "ws://127.0.0.1:7860/rpc"
SAETZE = Path(__file__).with_name("say_saetze.txt")


async def rufe(ws, nummer: int, methode: str, params: dict) -> dict:
    await ws.send(json.dumps({"jsonrpc": "2.0", "id": nummer, "method": methode, "params": params}))
    while True:
        antwort = json.loads(await asyncio.wait_for(ws.recv(), 15))
        if antwort.get("id") == nummer:
            return antwort


async def main(text: str) -> None:
    async with websockets.connect(ADRESSE, max_size=None) as ws:
        await rufe(ws, 1, "conversation.mic", {"muted": True})
        await asyncio.sleep(0.1)  # laufende Tonsendung zu Ende gehen lassen
        antwort = await rufe(ws, 2, "conversation.say", {"text": text})
        await rufe(ws, 3, "conversation.mic", {"muted": False})
    print(time.strftime("%T"), "gesendet:" if "error" not in antwort else "ABGELEHNT:", text)


if __name__ == "__main__":
    eingabe = sys.argv[1]
    zeilen = SAETZE.read_text(encoding="utf-8").splitlines()
    asyncio.run(main(zeilen[int(eingabe) - 1] if eingabe.isdigit() else eingabe))
