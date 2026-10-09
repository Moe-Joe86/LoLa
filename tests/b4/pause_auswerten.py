"""Pausenerkennung: Tabelle je Stufe aus den Ergebnissen von `pause_reihe.py`.

„Abgeschnitten“ heißt: Ein Ton der Antwort kam vor dem Ende der Aufnahme, es gab mehr als eine hörbare
Antwort, oder im zuletzt erkannten Text fehlt mehr als ein Viertel der Wörter des Satzes.
Aufruf: python3 pause_auswerten.py [<stufe> ...]
"""

import json
import re
import statistics
import sys
from pathlib import Path

MESSUNG = Path.home() / "lola-laufzeit/messung/pause"
SAETZE = (Path(__file__).parent / "testsaetze.txt").read_text(encoding="utf-8").splitlines()


def woerter(text: str) -> list[str]:
    return re.sub(r"[^\wäöüß ]", " ", text.lower()).split()


def toene(zeile: dict) -> list[float]:
    return [a["erster_ton"] for a in zeile["antworten"] if a["erster_ton"] is not None]


def abgeschnitten(zeile: dict) -> bool:
    soll = woerter(SAETZE[int(zeile["aufnahme"][5:7]) - 1])
    ist = woerter(zeile["erkannt"][-1]) if zeile["erkannt"] else []
    return len(toene(zeile)) > 1 or any(t < 0 for t in toene(zeile)) or len(ist) < 0.75 * len(soll)


def median(werte: list[float]) -> str:
    return f"{statistics.median(werte):.2f}" if werte else "–"


def stufe(name: str) -> str:
    daten = json.loads((MESSUNG / f"{name}.json").read_text(encoding="utf-8"))
    if "kurz" in daten:
        teile = []
        for nummer in range(1, 6):
            laeufe = [z for z in daten["kurz"] if z["aufnahme"] == f"satz_{nummer:02}"]
            erkannt = [z["erkannt"][-1] if z["erkannt"] else "–" for z in laeufe]
            zeit = median([t for z in laeufe for t in toene(z)])
            teile.append(f"{sum(bool(toene(z)) for z in laeufe)}/3 {erkannt} {zeit} s")
        return f"| {name} | " + " | ".join(teile) + " |"
    a1 = daten["a1"]
    erste = [toene(z)[0] for z in a1 if toene(z)]
    ja = a1[0]
    spalten = [
        name,
        f"{len(erste)}/20",
        median(erste),
        f"{max(erste):.2f}",
        f"{sum(abgeschnitten(z) for z in a1 if toene(z))}",
        f"{'ja' if toene(ja) else 'nein'} ({ja['erkannt'][-1] if ja['erkannt'] else '–'})",
    ]
    for pause in (300, 500, 700):
        gruppe = [z for z in daten["pause"] if z["aufnahme"].endswith(f"_{pause}")]
        letzte = [toene(z)[-1] for z in gruppe if toene(z)]
        spalten.append(f"{sum(abgeschnitten(z) for z in gruppe)}/{len(gruppe)} ({median(letzte)} s)")
    return "| " + " | ".join(spalten) + " |"


def main() -> None:
    namen = sys.argv[1:] or sorted(d.stem for d in MESSUNG.glob("*.json"))
    kurz = [n for n in namen if n.endswith("-kurz")]
    voll = [n for n in namen if not n.endswith("-kurz")]
    if voll:
        spalten = "beantwortet | erster Ton Median (s) | höchstens (s) | abgeschnitten | „Ja.“"
        print(f"| Stufe | {spalten} | Pause 0,3 s | 0,5 s | 0,7 s |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        print("\n".join(stufe(n) for n in voll))
    if kurz:
        print("\n| Stufe | Ja. | Nein, danke. | Okay. | Stopp! | Wie bitte? |\n| --- | --- | --- | --- | --- | --- |")
        print("\n".join(stufe(n) for n in kurz))


main()
