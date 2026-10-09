"""Zustandsbericht: der innere Zustand in einer Zeile für das Sprachmodell.

Reine Lesesicht (CLAUDE.md, Kreislauf-Regel 5): liest Charakter und Zustand, schreibt nie.
Form wie in A3 gemessen: Kennung, „Du, LoLa, bist …“, dann eine Sprechanweisung. Zustand und
Sprechanweisung kommen aus derselben festen Stufentabelle: keine Zahlen, keine freien Texte,
keine Beispielsätze (docs/KONZEPT.md).
"""

from seele.charakter import Charakter
from seele.zustand import Zustand

KENNUNG = "[Zustand]"
NAME = "LoLa"

# (obere Grenze, Zustand, Sprechanweisung): der erste Eintrag, dessen Grenze über dem Wert liegt, gilt.
LAUNE = [
    (-0.6, "bedrückt", "ernst"),
    (-0.2, "etwas gedrückter Stimmung", "zurückhaltend"),
    (0.2, "ausgeglichen", "sachlich"),
    (0.6, "gut gelaunt", "freundlich"),
    (float("inf"), "bester Laune", "herzlich"),
]
ERREGUNG = [
    (0.25, "ganz ruhig", "langsam und knapp, ohne Ausrufezeichen"),
    (0.5, "ruhig", "ruhig und knapp, ohne Ausrufezeichen"),
    (0.75, "lebhaft", "lebhaft"),
    (float("inf"), "aufgedreht", "schnell"),
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


def stufe(wert: float, stufen: list[tuple[float, str, str]]) -> tuple[str, str]:
    """Gibt zum Wert den Baustein für den Zustand und den für die Sprechanweisung zurück."""
    for grenze, zustand, sprechen in stufen:
        if wert < grenze:
            return zustand, sprechen
    return stufen[-1][1:]


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


def zustandsbericht(charakter: Charakter, zustand: Zustand, name: str = NAME) -> str:
    """Eine Zeile, die der Vermittler als eigenen Eintrag vor den letzten Nutzersatz setzt."""
    laune, ton = stufe(zustand.valenz, LAUNE)
    erregung, tempo = stufe(zustand.erregung, ERREGUNG)
    saetze = [f"Du, {name}, bist {laune} und {erregung}."]
    woerter = art(charakter)
    if woerter:
        saetze.append(f"Deine Art: {aufzaehlen(woerter)}.")
    saetze.append(f"Sprich {ton} und dabei {tempo}.")
    return " ".join([KENNUNG, *saetze])
