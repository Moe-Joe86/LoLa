"""Erklär-Log: jede Zustandsänderung mit Zeit, Auslöser, altem und neuem Wert.

Schutzregel 4 (docs/KONZEPT.md): Jede Änderung muss sich auf ihren Auslöser zurückführen lassen.
Vorerst nur im Speicher; eine Datei kommt hinzu, sobald der Vermittler läuft.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime


def jetzt() -> datetime:
    return datetime.now().astimezone()


@dataclass(frozen=True)
class Eintrag:
    zeit: datetime
    ausloeser: str
    groesse: str
    alt: float | None  # None beim Start, wenn es noch keinen alten Wert gibt
    neu: float


class ErklaerLog:
    def __init__(self, uhr: Callable[[], datetime] = jetzt) -> None:
        self._uhr = uhr
        self.eintraege: list[Eintrag] = []

    def schreiben(self, ausloeser: str, groesse: str, alt: float | None, neu: float) -> Eintrag:
        eintrag = Eintrag(self._uhr(), ausloeser, groesse, alt, neu)
        self.eintraege.append(eintrag)
        return eintrag
