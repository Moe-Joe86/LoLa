"""A5: baut die Blindprobe. Je Satz die Antworten der Modelle in zufälliger Reihenfolge, ohne Modellnamen.

Aufruf: python3 blindprobe.py <name> <name> ...   Schreibt blindprobe.md und, getrennt, zuordnung.json.
"""

import json
import random
import sys
from pathlib import Path

A5 = Path.home() / "lola-laufzeit/messung/a5"
NUMMERN = (6, 7, 8, 9, 10, 12, 15, 16, 17, 18, 19, 20)  # Sätze, die mehr als ein Wort Antwort verlangen


def main(namen: list[str]) -> None:
    daten = {n: json.loads((A5 / f"{n}.json").read_text(encoding="utf-8"))["saetze"] for n in namen}
    wuerfel = random.SystemRandom()
    zeilen, zuordnung = ["# Blindprobe A5 (Zustand: gut gelaunt und ruhig)", ""], {}
    for laufend, nummer in enumerate(NUMMERN, 1):
        reihenfolge = wuerfel.sample(namen, len(namen))
        satz = next(a["satz"] for a in daten[namen[0]] if a["nr"] == nummer and a["zustand"] == "gut")
        zeilen.append(f"**{laufend}. Du sagst: „{satz}“**")
        for buchstabe, name in zip("ABC", reihenfolge, strict=False):
            antwort = next(a for a in daten[name] if a["nr"] == nummer and a["zustand"] == "gut")
            zeilen.append(f"- {laufend}{buchstabe}: {antwort['text']}")
            zuordnung[f"{laufend}{buchstabe}"] = name
        zeilen.append("")
    (A5 / "blindprobe.md").write_text("\n".join(zeilen), encoding="utf-8")
    (A5 / "zuordnung.json").write_text(json.dumps(zuordnung, indent=1), encoding="utf-8")


main(sys.argv[1:])
