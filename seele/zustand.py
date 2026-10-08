"""Der innere Zustand. Nur diese Datei verändert ihn (CLAUDE.md, Kreislauf-Regel 2).

Vorerst nur die Stimmung: Valenz (-1 bedrückt bis +1 heiter) und Erregung (0 ruhig bis 1 aufgedreht).
Weitere Größen kommen erst, wenn ein beobachtetes Verhalten ohne sie fehlt.
"""

from dataclasses import dataclass, fields, replace

from seele.charakter import Charakter
from seele.erklaer_log import ErklaerLog

# Erregung in Ruhe. Kein Charakterwert, docs/KONZEPT.md nennt dafür keinen.
RUHE_ERREGUNG = 0.3

BEREICHE = {"valenz": (-1.0, 1.0), "erregung": (0.0, 1.0)}


@dataclass(frozen=True)
class Zustand:
    valenz: float
    erregung: float


def grundzustand(charakter: Charakter, log: ErklaerLog) -> Zustand:
    """Startzustand: Valenz auf der Grundstimmung, Erregung in Ruhe."""
    zustand = Zustand(valenz=2.0 * charakter.grundstimmung - 1.0, erregung=RUHE_ERREGUNG)
    for feld in fields(Zustand):
        log.schreiben("Start aus dem Charakter", feld.name, None, getattr(zustand, feld.name))
    return zustand


def aendern(zustand: Zustand, log: ErklaerLog, ausloeser: str, **neue_werte: float) -> Zustand:
    """Gibt den neuen Zustand zurück. Werte außerhalb des Bereichs werden auf die Grenze gesetzt.

    Jede tatsächliche Änderung landet im Erklär-Log, unveränderte Werte nicht.
    """
    unbekannt = set(neue_werte) - set(BEREICHE)
    if unbekannt:
        raise ValueError(f"unbekannte Zustandsgrößen: {', '.join(sorted(unbekannt))}")
    if not ausloeser:
        raise ValueError("eine Zustandsänderung braucht einen Auslöser")
    begrenzt = {}
    for groesse, wert in neue_werte.items():
        unten, oben = BEREICHE[groesse]
        neu = min(max(wert, unten), oben)
        alt = getattr(zustand, groesse)
        if neu != alt:
            log.schreiben(ausloeser, groesse, alt, neu)
            begrenzt[groesse] = neu
    return replace(zustand, **begrenzt)
