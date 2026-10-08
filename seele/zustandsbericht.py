"""Zustandsbericht: der innere Zustand in wenigen Worten für das Sprachmodell.

Reine Lesesicht (CLAUDE.md, Kreislauf-Regel 5): liest Charakter und Zustand, schreibt nie.
Feste Stufen mit festen Satzbausteinen, keine Zahlen im Text (docs/KONZEPT.md).
"""

from seele.charakter import Charakter
from seele.zustand import Zustand

KOPF = "Innerer Zustand (nicht vorlesen, nur danach handeln):"
KUERZE = "Halte dich kurz, höchstens zwei Sätze."

# (obere Grenze, Baustein): der erste Eintrag, dessen Grenze über dem Wert liegt, gilt.
LAUNE = [
    (-0.6, "bedrückt"),
    (-0.2, "etwas gedrückter Stimmung"),
    (0.2, "ausgeglichen"),
    (0.6, "gut gelaunt"),
    (float("inf"), "bester Laune"),
]
ERREGUNG = [
    (0.25, "ganz ruhig"),
    (0.5, "ruhig"),
    (0.75, "lebhaft"),
    (float("inf"), "aufgedreht"),
]

# Nur Werte, die das Verhalten im Gespräch prägen. Grundstimmung, Reaktivität und
# Rückkehrstärke wirken über den Zustand, nicht über Worte.
ART = {
    "geselligkeit": ("zurückhaltend", "gesellig"),
    "neugier": ("wenig neugierig", "neugierig"),
    "vorsicht": ("unbefangen", "vorsichtig"),
    "ausdauer": ("sprunghaft", "ausdauernd"),
}
ART_NIEDRIG = 0.35  # bis hierher gilt der erste Baustein
ART_HOCH = 0.65  # ab hier der zweite; dazwischen wird der Wert nicht erwähnt


def stufe(wert: float, stufen: list[tuple[float, str]]) -> str:
    for grenze, baustein in stufen:
        if wert < grenze:
            return baustein
    return stufen[-1][1]


def aufzaehlen(woerter: list[str]) -> str:
    if len(woerter) <= 1:
        return "".join(woerter)
    return ", ".join(woerter[:-1]) + " und " + woerter[-1]


def art(charakter: Charakter) -> list[str]:
    woerter = []
    for name, (niedrig, hoch) in ART.items():
        wert = getattr(charakter, name)
        if wert <= ART_NIEDRIG:
            woerter.append(niedrig)
        elif wert >= ART_HOCH:
            woerter.append(hoch)
    return woerter


def zustandsbericht(charakter: Charakter, zustand: Zustand) -> str:
    zeilen = [f"Du bist {stufe(zustand.valenz, LAUNE)} und {stufe(zustand.erregung, ERREGUNG)}."]
    woerter = art(charakter)
    if woerter:
        zeilen.append(f"Deine Art: {aufzaehlen(woerter)}.")
    zeilen.append(KUERZE)
    return "\n".join([KOPF, *(f"- {zeile}" for zeile in zeilen)])
