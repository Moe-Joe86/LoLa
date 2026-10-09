"""Erklär-Log: jede Zustandsänderung mit Zeit, Auslöser, altem und neuem Wert.

Schutzregel 4 (docs/KONZEPT.md): Jede Änderung muss sich auf ihren Auslöser zurückführen lassen.
Die Einträge stehen im Speicher und, wenn eine Datei angegeben ist, dort als eine Zeile JSON je Eintrag.
Die Datei wird nie gekürzt: Sie enthält Zustandswerte und Auslöser, nichts Gesagtes.
"""

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


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
    def __init__(self, uhr: Callable[[], datetime] = jetzt, datei: Path | None = None) -> None:
        self._uhr = uhr
        self._datei = datei
        self.eintraege: list[Eintrag] = []

    def schreiben(self, ausloeser: str, groesse: str, alt: float | None, neu: float) -> Eintrag:
        eintrag = Eintrag(self._uhr(), ausloeser, groesse, alt, neu)
        self.eintraege.append(eintrag)
        if self._datei is not None:
            self._datei.parent.mkdir(parents=True, exist_ok=True)
            zeile = asdict(eintrag) | {"zeit": eintrag.zeit.isoformat()}
            with self._datei.open("a", encoding="utf-8") as datei:
                datei.write(json.dumps(zeile, ensure_ascii=False) + "\n")
        return eintrag
