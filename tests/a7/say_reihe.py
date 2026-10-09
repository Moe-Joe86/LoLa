"""Schleust eine Reihe von Saetzen ueber conversation.say ein, wahlweise mit stummem Mikrofon beim Senden.

Aufruf (Umgebung mit `websockets`): python tests/a7/say_reihe.py <Anzahl> <normal|stumm> [Abstand in s]
"""

import asyncio
import json
import sys
import time

import websockets

ADRESSE = "ws://127.0.0.1:7860/rpc"
SATZ = "Sag bitte nur das Wort Ja."


async def rufe(ws, nummer: int, methode: str, params: dict) -> dict:
    await ws.send(json.dumps({"jsonrpc": "2.0", "id": nummer, "method": methode, "params": params}))
    while True:
        antwort = json.loads(await asyncio.wait_for(ws.recv(), 15))
        if antwort.get("id") == nummer:
            return antwort


async def main(anzahl: int, art: str, abstand: float) -> None:
    fehler = 0
    async with websockets.connect(ADRESSE, max_size=None) as ws:
        for runde in range(anzahl):
            await asyncio.sleep(abstand)
            if art == "stumm":
                await rufe(ws, 3 * runde + 1, "conversation.mic", {"muted": True})
                await asyncio.sleep(0.1)  # laufende Tonsendung zu Ende gehen lassen
            antwort = await rufe(ws, 3 * runde + 2, "conversation.say", {"text": SATZ})
            if art == "stumm":
                await rufe(ws, 3 * runde + 3, "conversation.mic", {"muted": False})
            if "error" in antwort:
                fehler += 1
                print(time.strftime("%T"), runde + 1, antwort["error"].get("message"))
    print(f"{art}: {anzahl} Sätze gesendet, {fehler} vom /rpc abgelehnt")


if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]), sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 4.0))
