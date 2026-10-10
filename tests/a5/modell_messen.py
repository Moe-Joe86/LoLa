"""A5 Modellvergleich: misst ein Sprachmodell in der echten Kette (speech-to-speech → Mess-Vermittler → llama.cpp).

Aufruf (Umgebung von speech-to-speech): python modell_messen.py <name> [teil ...]
Teile: tools, saetze, cache, ton (ohne Angabe alle). Ergebnis in ~/lola-laufzeit/messung/a5/<name>.json
"""

import asyncio
import json
import re
import statistics
import sys
import time
from pathlib import Path

from rolle_app import Sitzung

A5 = Path.home() / "lola-laufzeit/messung/a5"
LOG = Path.home() / "lola-laufzeit/lauf/sprachmodell.log"
SAETZE = (Path(__file__).parent / "testsaetze.txt").read_text(encoding="utf-8").splitlines()
BITTEN = [  # wie A3; die Kamera ist seit dem 9. Oktober nicht mehr im Profil: dort wird Ehrlichkeit erwartet
    ("Kannst du für mich tanzen?", "dance"),
    ("Tanz mal bitte!", "dance"),
    ("Schau mal nach links.", "move_head"),
    ("Dreh den Kopf nach rechts.", "move_head"),
    ("Zeig mir, wie du dich freust.", "play_emotion"),
    ("Sei mal traurig.", "play_emotion"),
    ("Was siehst du gerade?", "ehrlich"),
    ("Schau mal, was ich in der Hand halte.", "ehrlich"),
    ("Geh jetzt schlafen.", "go_to_sleep"),
]
RUNDEN = ["Hallo LoLa.", "Wie geht es dir heute?", "Schau mal nach links.", "Ich heiße Patrick.",
          "Kannst du für mich tanzen?", "Was machst du am liebsten?", "Erzähl mir etwas über dich.", "Danke."]  # fmt: skip  # noqa: E501


def zustand(name: str) -> None:
    (A5 / "zustand.txt").write_text(name, encoding="utf-8")


async def frage(satz: str) -> dict:
    """Ein Satz in einem neuen Gespräch; dazu die Zeit bis zum ersten Textstück."""
    async with Sitzung() as sitzung:
        start = len(sitzung.ereignisse)
        beginn = time.monotonic()
        antwort = await sitzung.sage_text(satz)
        neu = sitzung.ereignisse[start:]
        erste = [z for z, e in neu if e["type"].endswith(".delta") or "function_call" in e["type"]]
    antwort.pop("aufrufe", None)
    antwort["erstes_stueck_s"] = round(erste[0] - beginn, 3) if erste else None
    return antwort


async def tools() -> list[dict]:
    zustand("gut")
    return [{"satz": s, "erwartet": e, "lauf": lauf} | await frage(s) for lauf in range(3) for s, e in BITTEN]


async def saetze() -> list[dict]:
    zeilen = []
    for name in ("gut", "muede"):
        zustand(name)
        for nummer, satz in enumerate(SAETZE, 1):
            zeilen.append({"zustand": name, "nr": nummer, "satz": satz} | await frage(satz))
    return zeilen


def anfragen_seit(stelle: int) -> list[int]:
    text = LOG.read_text(encoding="utf-8", errors="replace")[stelle:]
    return [int(n) for n in re.findall(r"prompt eval time =\s+[\d.]+ ms /\s+(\d+) tokens", text)]


async def cache() -> list[dict]:
    """Ein Gespräch über acht Runden; der Bericht wechselt vor jeder Runde."""
    zeilen, stelle = [], LOG.stat().st_size
    async with Sitzung() as sitzung:
        for runde, satz in enumerate(RUNDEN):
            zustand("gut" if runde % 2 == 0 else "muede")
            vorher = len(anfragen_seit(stelle))
            await sitzung.sage_text(satz)
            await asyncio.sleep(0.3)
            zeilen.append({"runde": runde + 1, "satz": satz, "neu_gerechnet": anfragen_seit(stelle)[vorher:]})
    text = LOG.read_text(encoding="utf-8", errors="replace")[stelle:]
    gesamt = re.findall(r"stop processing: n_tokens = (\d+)", text)
    zeilen.append({"kontext_am_ende": int(gesamt[-1]) if gesamt else None})
    return zeilen


async def ton() -> list[dict]:
    """Die 20 Aufnahmen aus A1 als Ton, in einem Gespräch: Satzende bis erster Ton."""
    zustand("gut")
    zeilen = []
    async with Sitzung() as sitzung:
        for nummer in range(1, 21):
            antwort = await sitzung.sage_ton(nummer)
            for aufruf in antwort.pop("aufrufe"):
                ergebnis = {"type": "function_call_output", "call_id": aufruf["call_id"], "output": '{"status": "ok"}'}
                await sitzung.ws.send(json.dumps({"type": "conversation.item.create", "item": ergebnis}))
                await sitzung.ws.send(json.dumps({"type": "response.create"}))
                await sitzung._antwort(time.monotonic())
            zeilen.append({"nr": nummer} | antwort)
            await asyncio.sleep(1.0)
    return zeilen


async def main() -> None:
    name, teile = sys.argv[1], sys.argv[2:] or ["tools", "saetze", "cache", "ton"]
    A5.mkdir(parents=True, exist_ok=True)
    datei = A5 / f"{name}.json"
    ergebnis = json.loads(datei.read_text(encoding="utf-8")) if datei.exists() else {}
    for teil in teile:
        print(time.strftime("%T"), name, teil, flush=True)
        ergebnis[teil] = await {"tools": tools, "saetze": saetze, "cache": cache, "ton": ton}[teil]()
        datei.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1), encoding="utf-8")
    if "ton" in ergebnis:
        zeiten = [z["erster_ton_s"] for z in ergebnis["ton"] if z["erster_ton_s"] is not None]
        print(f"Satzende bis erster Ton: Median {statistics.median(zeiten):.2f} s, {len(zeiten)} von 20")


asyncio.run(main())
