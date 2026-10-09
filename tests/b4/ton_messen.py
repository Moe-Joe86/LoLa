"""B4: die 20 Aufnahmen aus A1 als Ton durch die echte Kette, in einem Gespräch.

Zeigt je Satz, was erkannt wurde, die Zeit vom Satzende bis zum ersten Ton der Antwort und die Tool-Aufrufe.
Aufruf: python ton_messen.py
"""

import asyncio
import json
import statistics
import time
from pathlib import Path

from rolle_app import Sitzung

SAETZE = (Path(__file__).parent / "testsaetze.txt").read_text(encoding="utf-8").splitlines()


async def main() -> None:
    zeilen, zeiten = [], []
    print(time.strftime("Beginn %T"))
    async with Sitzung() as sitzung:
        for nummer in range(1, 21):
            antwort = await sitzung.sage_ton(nummer)
            for aufruf in antwort.pop("aufrufe"):  # Tool-Ergebnis wie die App zurückmelden
                ergebnis = {"type": "function_call_output", "call_id": aufruf["call_id"], "output": '{"status": "ok"}'}
                await sitzung.ws.send(json.dumps({"type": "conversation.item.create", "item": ergebnis}))
                await sitzung.ws.send(json.dumps({"type": "response.create"}))
                await sitzung._antwort(time.monotonic())
            zeilen.append({"nummer": nummer, "soll": SAETZE[nummer - 1]} | antwort)
            if antwort["erster_ton_s"] is not None:
                zeiten.append(antwort["erster_ton_s"])
            print(
                f"{nummer:2} | {SAETZE[nummer - 1][:34]:34} | erkannt: {antwort['erkannt'][:34]:34} | "
                f"erster Ton {antwort['erster_ton_s']} s | {[t[0] for t in antwort['tools']]} | {antwort['text'][:40]}"
            )
            await asyncio.sleep(1.0)
    print(time.strftime("Ende %T"))
    print(
        f"Satzende bis erster Ton: Mittel {statistics.mean(zeiten):.2f} s, Median {statistics.median(zeiten):.2f} s, "
        f"höchstens {max(zeiten):.2f} s ({len(zeiten)} Sätze)"
    )
    ziel = Path.home() / "lola-laufzeit/messung/b4/ton.json"
    ziel.write_text(json.dumps(zeilen, ensure_ascii=False, indent=1), encoding="utf-8")


asyncio.run(main())
