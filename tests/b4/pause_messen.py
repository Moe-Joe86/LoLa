"""B4: Sprechpause mitten im Satz. Löst das eine vorgreifende Anfrage ans Sprachmodell aus?

Zwei Aufnahmen mit einer Pause dazwischen, je Pause eine eigene Sitzung. Aufruf: python pause_messen.py
"""

import asyncio
import time

from rolle_app import Sitzung


async def main() -> None:
    for pause in (0.7, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.6):
        async with Sitzung() as sitzung:
            beginn = time.strftime("%T")
            antwort = await sitzung.sage_ton(7, danach=10, pause=pause)
            await asyncio.sleep(4)  # eine zweite Antwort kann noch folgen
            print(
                f"{beginn} Pause {pause} s | erkannt: {antwort['erkannt']} | Antwort: {antwort['text'][:60]}",
                flush=True,
            )


asyncio.run(main())
