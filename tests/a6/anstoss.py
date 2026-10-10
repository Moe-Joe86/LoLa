"""A6: schickt einen Anstoß über conversation.say, mit der Abhilfe aus A7 (Mikrofon stumm, 0,1 s warten, senden,
Mikrofon an), und schreibt Zeit und Wortlaut in ~/lola-laufzeit/messung/a6/anstoesse.jsonl.

Aufruf (Umgebung mit `websockets`): python tests/a6/anstoss.py <Buchstabe aus ANSTOESSE | "freier Text">
"""

import asyncio
import json
import sys
import time
from pathlib import Path

import websockets

ADRESSE = "ws://127.0.0.1:7860/rpc"
ZIEL = Path.home() / "lola-laufzeit/messung/a6/anstoesse.jsonl"
ANSTOESSE = {
    "a": "Begrüße Patrick, er ist gerade ins Zimmer gekommen.",
    "b": "Frag Patrick, wie sein Tag war.",
    "c": "Erzähl Patrick kurz etwas, das dich heute interessiert hat.",
    "d": "Erinnere Patrick freundlich, dass er etwas trinken sollte.",
    "e": "Sag Patrick, dass du dich freust, dass er da ist.",
}


async def rufe(ws, nummer: int, methode: str, params: dict) -> dict:
    await ws.send(json.dumps({"jsonrpc": "2.0", "id": nummer, "method": methode, "params": params}))
    while True:
        antwort = json.loads(await asyncio.wait_for(ws.recv(), 15))
        if antwort.get("id") == nummer:
            return antwort


async def main(kennung: str) -> None:
    text = ANSTOESSE.get(kennung, kennung)
    async with websockets.connect(ADRESSE, max_size=None) as ws:
        await rufe(ws, 1, "conversation.mic", {"muted": True})
        await asyncio.sleep(0.1)  # laufende Tonsendung zu Ende gehen lassen
        gesendet = time.time()
        antwort = await rufe(ws, 2, "conversation.say", {"text": text})
        await rufe(ws, 3, "conversation.mic", {"muted": False})
    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    zeile = {"zeit": time.strftime("%T", time.localtime(gesendet)), "t": gesendet, "kennung": kennung, "text": text,
             "abgelehnt": "error" in antwort}  # fmt: skip
    with ZIEL.open("a", encoding="utf-8") as datei:
        datei.write(json.dumps(zeile, ensure_ascii=False) + "\n")
    print(zeile["zeit"], "ABGELEHNT:" if zeile["abgelehnt"] else "gesendet:", text)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
