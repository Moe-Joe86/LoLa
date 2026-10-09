"""Wertet die gesprochenen Testsaetze aus dem Log der Conversation App aus (nur lesen).

Aufruf: python tests/a4/saetze_auswerten.py <app.log> [ab HH:MM:SS]
Erwartet: Jeder Testsatz wurde einmal gesprochen, in der Reihenfolge von testsaetze.txt.
"""

import re
import statistics
import sys
from pathlib import Path

SAETZE = Path(__file__).with_name("testsaetze.txt")
ZEIT = r"(\d\d:\d\d:\d\d),\d+ "


def woerter(text: str) -> list[str]:
    return re.sub(r"[^\wäöüß ]", " ", text.lower()).split()


def wortfehler(soll: list[str], ist: list[str]) -> int:
    """Kleinste Zahl an Ersetzungen, Einfuegungen und Auslassungen (Levenshtein auf Woertern)."""
    zeile = list(range(len(ist) + 1))
    for i, wort in enumerate(soll, 1):
        neu = [i]
        for j, anderes in enumerate(ist, 1):
            neu.append(min(zeile[j] + 1, neu[j - 1] + 1, zeile[j - 1] + (wort != anderes)))
        zeile = neu
    return zeile[-1]


def lies_log(text: str, ab: str = "00:00:00") -> tuple[list[str], list[int]]:
    """Gibt die erkannten Nutzersaetze und die Zeiten bis zum ersten Ton (ms) zurueck."""
    erkannt, latenzen = [], []
    for zeile in text.splitlines():
        zeit = re.search(ZEIT, zeile)
        if not zeit or zeit.group(1) < ab:
            continue
        if treffer := re.search(r"role=user content=(.*)", zeile):
            erkannt.append(treffer.group(1).strip())
        elif treffer := re.search(r"first audio delta (\d+) ms after user transcript", zeile):
            latenzen.append(int(treffer.group(1)))
    return erkannt, latenzen


def main() -> int:
    soll = SAETZE.read_text(encoding="utf-8").splitlines()
    erkannt, latenzen = lies_log(Path(sys.argv[1]).read_text(encoding="utf-8"), *sys.argv[2:3])
    if len(erkannt) != len(soll):
        print(f"{len(erkannt)} erkannte Sätze, {len(soll)} erwartet. Zuordnung von Hand prüfen:")
        print("\n".join(f"  {nr:2} {satz}" for nr, satz in enumerate(erkannt, 1)))
        return 1
    fehler = gesamt = 0
    for nr, (s, e) in enumerate(zip(soll, erkannt, strict=True), 1):
        f = wortfehler(woerter(s), woerter(e))
        fehler, gesamt = fehler + f, gesamt + len(woerter(s))
        print(f"{nr:2} {f} Fehler | {s} | {e}")
    print(f"\nWortfehler: {fehler} von {gesamt}")
    if latenzen:
        print(f"Erkannter Text bis erster Ton an der App: Mittel {statistics.mean(latenzen):.0f} ms, "
              f"höchstens {max(latenzen)} ms ({len(latenzen)} Runden). Ohne Pausenerkennung und Funkstrecke.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
