"""Lädt die Charakterdatei und prüft sie.

Der Charakter ist reine Konfiguration (CLAUDE.md, Kreislauf-Regel 4). Diese Datei liest ihn
nur ein und weist fehlende, unbekannte oder ungültige Werte zurück.
"""

import tomllib
from dataclasses import dataclass, fields
from pathlib import Path

STANDARD_DATEI = Path(__file__).resolve().parent.parent / "charakter" / "reachy.toml"


class CharakterFehler(ValueError):
    """Die Charakterdatei ist unvollständig oder enthält ungültige Werte."""


@dataclass(frozen=True)
class Charakter:
    """Die sieben festen Charakterwerte aus docs/KONZEPT.md, jeweils zwischen 0 und 1."""

    grundstimmung: float
    reaktivitaet: float
    rueckkehrstaerke: float
    geselligkeit: float
    neugier: float
    vorsicht: float
    ausdauer: float


def charakter_laden(datei: Path = STANDARD_DATEI) -> Charakter:
    with datei.open("rb") as f:
        werte = tomllib.load(f)
    return charakter_pruefen(werte)


def charakter_pruefen(werte: dict) -> Charakter:
    """Sammelt alle Probleme auf einmal, damit ein Lauf alle Fehler in der Datei zeigt."""
    namen = [feld.name for feld in fields(Charakter)]
    probleme = []
    fehlend = [name for name in namen if name not in werte]
    if fehlend:
        probleme.append(f"fehlende Werte: {', '.join(fehlend)}")
    unbekannt = sorted(set(werte) - set(namen))
    if unbekannt:
        probleme.append(f"unbekannte Werte: {', '.join(unbekannt)}")
    for name in namen:
        if name not in werte:
            continue
        wert = werte[name]
        if isinstance(wert, bool) or not isinstance(wert, int | float):
            probleme.append(f"{name} ist keine Zahl: {wert!r}")
        elif not 0.0 <= wert <= 1.0:
            probleme.append(f"{name} = {wert} liegt nicht zwischen 0 und 1")
    if probleme:
        raise CharakterFehler("; ".join(probleme))
    return Charakter(**{name: float(werte[name]) for name in namen})
