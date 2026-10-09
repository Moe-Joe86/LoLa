"""Pausenerkennung: spielt die 20 Aufnahmen aus A1 und die Aufnahmen mit Denkpause ein und schreibt je
Aufnahme auf, wann was zurückkam. Zeiten in Sekunden, bezogen auf das Ende der Aufnahme.

Aufruf (Umgebung von speech-to-speech): python pause_reihe.py <name-der-stufe> [kurz]
Mit `kurz` nur die fünf kurzen Sätze, je dreimal.
"""

import asyncio
import base64
import json
import sys
import time
import wave
from pathlib import Path

from rolle_app import AUFNAHMEN, STUECK, Sitzung

MESSUNG = Path.home() / "lola-laufzeit/messung/pause"
TAKT = 0.02
RUHE_S = 2.0  # so lange muss nach der letzten Antwort nichts mehr kommen
MINDESTENS_S = 5.0  # so lange nach dem Ende der Aufnahme wird mindestens gewartet
HOECHSTENS_S = 30.0


def lade(datei: Path) -> bytes:
    with wave.open(str(datei)) as ton:
        assert (ton.getframerate(), ton.getnchannels(), ton.getsampwidth()) == (16000, 1, 2)
        return ton.readframes(ton.getnframes())


async def lies(sitzung: Sitzung, ereignisse: list[tuple[float, dict]]) -> None:
    """Liest alles mit und meldet Tool-Aufrufe wie die App als erledigt zurück."""
    aufrufe = []
    async for roh in sitzung.ws:
        ereignis = json.loads(roh)
        ereignisse.append((time.monotonic(), ereignis))
        if ereignis["type"] == "response.output_item.done" and ereignis["item"]["type"] == "function_call":
            aufrufe.append(ereignis["item"]["call_id"])
        if ereignis["type"] == "response.done" and aufrufe:
            for kennung in aufrufe:
                ergebnis = {"type": "function_call_output", "call_id": kennung, "output": '{"status": "ok"}'}
                await sitzung.ws.send(json.dumps({"type": "conversation.item.create", "item": ergebnis}))
            await sitzung.ws.send(json.dumps({"type": "response.create"}))
            aufrufe = []


def fertig(ereignisse: list[tuple[float, dict]], ab: int, ende: float) -> bool:
    """Ruhe: genug Zeit seit dem Ende der Aufnahme, keine Antwort mehr unterwegs, nichts Neues mehr."""
    jetzt = time.monotonic()
    neu = ereignisse[ab:]
    offen = sum(e["type"] == "response.created" for _, e in neu) - sum(e["type"] == "response.done" for _, e in neu)
    letztes = neu[-1][0] if neu else ende
    return jetzt - ende >= MINDESTENS_S and offen <= 0 and jetzt - letztes >= RUHE_S


async def spiele(sitzung: Sitzung, ereignisse: list, daten: bytes) -> dict:
    """Spielt eine Aufnahme im Takt der echten Zeit, danach Stille, bis Ruhe ist."""
    ab = len(ereignisse)
    stille = bytes(2 * STUECK)
    takt = time.monotonic()
    ende = takt + len(daten) / 32000
    stelle = 0
    while not (stelle >= len(daten) and (fertig(ereignisse, ab, ende) or time.monotonic() - ende > HOECHSTENS_S)):
        stueck = (daten[stelle : stelle + 2 * STUECK] or stille).ljust(2 * STUECK, b"\0")
        stelle += 2 * STUECK
        ton = base64.b64encode(stueck).decode()
        await sitzung.ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": ton}))
        takt += TAKT
        await asyncio.sleep(max(takt - time.monotonic(), 0))
    neu = ereignisse[ab:]

    def zeiten(art: str) -> list[float]:
        return [round(zeit - ende, 2) for zeit, e in neu if e["type"].endswith(art)]

    antworten, laufend = [], None
    for zeit, e in neu:
        if e["type"] == "response.created":
            laufend = {"beginn": round(zeit - ende, 2), "erster_ton": None, "text": ""}
            antworten.append(laufend)
        elif laufend and e["type"] == "response.output_audio.delta" and laufend["erster_ton"] is None:
            laufend["erster_ton"] = round(zeit - ende, 2)
        elif laufend and e["type"].endswith("transcript.delta"):
            laufend["text"] += e.get("delta", "")
    return {
        "sprache_beginn": zeiten("speech_started"),
        "sprache_ende": zeiten("speech_stopped"),
        "erkannt": [e.get("transcript", "") for _, e in neu if e["type"].endswith("transcription.completed")],
        "antworten": antworten,
    }


async def reihe(aufnahmen: list[tuple[str, Path]]) -> list[dict]:
    zeilen = []
    async with Sitzung() as sitzung:
        ereignisse: list[tuple[float, dict]] = []
        leser = asyncio.create_task(lies(sitzung, ereignisse))
        for name, datei in aufnahmen:
            zeile = {"aufnahme": name} | await spiele(sitzung, ereignisse, lade(datei))
            toene = [a["erster_ton"] for a in zeile["antworten"] if a["erster_ton"] is not None]
            print(f"{name:20} erkannt {zeile['erkannt']} | erster Ton {toene}", flush=True)
            zeilen.append(zeile)
        leser.cancel()
    return zeilen


async def main() -> None:
    stufe = sys.argv[1]
    if sys.argv[2:] == ["kurz"]:
        gruppen = {"kurz": [(f"satz_{n:02}", AUFNAHMEN / f"satz_{n:02}.wav") for n in (1, 2, 3, 4, 5)] * 3}
    else:
        gruppen = {
            "a1": [(f"satz_{n:02}", AUFNAHMEN / f"satz_{n:02}.wav") for n in range(1, 21)],
            "pause": [(d.stem, d) for d in sorted((MESSUNG / "aufnahmen").glob("*_pause_*.wav"))],
        }
    ergebnis = {name: await reihe(aufnahmen) for name, aufnahmen in gruppen.items()}
    (MESSUNG / f"{stufe}.json").write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1), encoding="utf-8")


asyncio.run(main())
