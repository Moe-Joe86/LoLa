"""B4: Wie viele Eingabe-Token rechnet llama.cpp je Anfrage neu? Ein Gespräch über acht Runden.

Liest dazu das Log von llama.cpp (`prompt eval time … / N tokens` und `n_tokens = …`). Aufruf: python zwischenspeicher.py
"""

import asyncio
import re
from pathlib import Path

from rolle_app import Sitzung

LOG = Path.home() / "lola-laufzeit/lauf/sprachmodell.log"
RUNDEN = [
    "Hallo LoLa.",
    "Wie geht es dir heute?",
    "Schau mal nach links.",
    "Ich heiße Patrick.",
    "Kannst du für mich tanzen?",
    "Was machst du am liebsten?",
    "Erzähl mir etwas über dich.",
    "Danke, das war schön.",
]


def anfragen_seit(stelle: int) -> list[tuple[int, int]]:
    """Je Anfrage: neu gerechnete Eingabe-Token und Token insgesamt nach der Antwort."""
    text = LOG.read_text(encoding="utf-8", errors="replace")[stelle:]
    neu = [int(n) for n in re.findall(r"prompt eval time =\s+[\d.]+ ms /\s+(\d+) tokens", text)]
    gesamt = [int(n) for n in re.findall(r"stop processing: n_tokens = (\d+)", text)]
    return list(zip(neu, gesamt, strict=False))


async def main() -> None:
    stelle = LOG.stat().st_size
    async with Sitzung() as sitzung:
        for runde, satz in enumerate(RUNDEN, 1):
            vorher = len(anfragen_seit(stelle))
            antwort = await sitzung.sage_text(satz)
            await asyncio.sleep(0.3)
            for neu, gesamt in anfragen_seit(stelle)[vorher:]:
                print(
                    f"Runde {runde} | {satz[:28]:28} | neu gerechnet {neu:5} | Kontext danach {gesamt:5} | "
                    f"{'Tool' if antwort['tools'] else 'Text'}"
                )


asyncio.run(main())
