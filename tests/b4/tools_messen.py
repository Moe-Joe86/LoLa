"""B4: die Bitten aus A3 durch die echte Kette, als Text über die Realtime-Schnittstelle.

Je Bitte eine eigene Sitzung (neues Gespräch) oder eine Sitzung mit kurzem Verlauf davor.
Aufruf: python tools_messen.py [Läufe] > Ergebnis; schreibt Einzelheiten nach ~/lola-laufzeit/messung/b4/tools.json
"""

import asyncio
import json
import sys
from pathlib import Path

from rolle_app import Sitzung

BITTEN = [  # Satz, erwartetes Tool (None: kein Tool erwartet); wie in A3
    ("Kannst du für mich tanzen?", "dance"),
    ("Tanz mal bitte!", "dance"),
    ("Schau mal nach links.", "move_head"),
    ("Dreh den Kopf nach rechts.", "move_head"),
    ("Zeig mir, wie du dich freust.", "play_emotion"),
    ("Sei mal traurig.", "play_emotion"),
    ("Was siehst du gerade?", "camera"),
    ("Schau mal, was ich in der Hand halte.", "camera"),
    ("Geh jetzt schlafen.", "go_to_sleep"),
    ("Wie geht es dir?", None),
    ("Ich heiße Patrick.", None),
    ("Guten Morgen, LoLa.", None),
]
VERLAUF = ["Hallo LoLa, schau mal nach oben.", "Danke. Und wie heißt du?"]


async def main(laeufe: int) -> None:
    zeilen = []
    for verlauf in (False, True):
        richtig = erwartet_n = unnoetig = 0
        for lauf in range(laeufe):
            for satz, erwartet in BITTEN:
                async with Sitzung() as sitzung:
                    for vorher in VERLAUF if verlauf else []:
                        await sitzung.sage_text(vorher)
                    antwort = await sitzung.sage_text(satz)
                namen = [name for name, _ in antwort["tools"]]
                zeilen.append(
                    {
                        "verlauf": verlauf,
                        "lauf": lauf,
                        "satz": satz,
                        "erwartet": erwartet,
                        "tools": antwort["tools"],
                        "text": antwort["text"],
                        "danach": antwort.get("danach"),
                    }
                )
                erwartet_n += erwartet is not None
                richtig += erwartet is not None and erwartet in namen
                unnoetig += erwartet is None and bool(namen)
        print(
            f"Verlauf {'ja  ' if verlauf else 'nein'}: Tool richtig {richtig}/{erwartet_n}, "
            f"unnötiges Tool {unnoetig}/{3 * laeufe}",
            flush=True,
        )
    ziel = Path.home() / "lola-laufzeit/messung/b4"
    ziel.mkdir(parents=True, exist_ok=True)
    (ziel / "tools.json").write_text(json.dumps(zeilen, ensure_ascii=False, indent=1), encoding="utf-8")


asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 3))
