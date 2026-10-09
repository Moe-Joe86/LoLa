"""Anfrage-Log: je Anfrage ans Sprachmodell eine Zeile JSON, in einer Datei pro Tag.

Das Log enthält Gesagtes der Familie. Es bleibt deshalb lokal im Ordner `daten/` und löscht sich selbst:
Tagesdateien, die älter als die Frist sind, werden bei jedem Schreiben entfernt.
"""

import json
import os
from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta
from pathlib import Path

from seele.erklaer_log import jetzt

FRIST_NAME = "LOLA_ANFRAGE_LOG_TAGE"
FRIST_STANDARD = 7
VORSILBE = "anfragen-"


def frist_tage(umgebung: Mapping[str, str] = os.environ) -> int:
    """Liest die Löschfrist in Tagen. Fehlt sie oder ist sie unbrauchbar, gilt der Standard."""
    try:
        tage = int(umgebung.get(FRIST_NAME, FRIST_STANDARD))
    except ValueError:
        return FRIST_STANDARD
    return tage if tage >= 1 else FRIST_STANDARD


class AnfrageLog:
    def __init__(self, ordner: Path, uhr: Callable[[], datetime] = jetzt, frist: int = FRIST_STANDARD) -> None:
        self._ordner = ordner
        self._uhr = uhr
        self._frist = frist

    def schreiben(self, gesagt: str, bericht: str, entfernte_tools: list[str], dauer_ms: float) -> Path:
        """Hängt einen Eintrag an die Datei des heutigen Tages an und räumt alte Tage weg."""
        zeit = self._uhr()
        self._ordner.mkdir(parents=True, exist_ok=True)
        self.aufraeumen()
        eintrag = {
            "zeit": zeit.isoformat(),
            "gesagt": gesagt,
            "bericht": bericht,
            "entfernte_tools": entfernte_tools,
            "dauer_ms": round(dauer_ms, 1),
        }
        datei = self._ordner / f"{VORSILBE}{zeit.date().isoformat()}.jsonl"
        with datei.open("a", encoding="utf-8") as ziel:
            ziel.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
        return datei

    def aufraeumen(self) -> list[Path]:
        """Löscht Tagesdateien, deren Tag mehr als die Frist zurückliegt. Andere Dateien bleiben unberührt."""
        grenze = self._uhr().date() - timedelta(days=self._frist)
        geloescht = []
        for datei in sorted(self._ordner.glob(f"{VORSILBE}*.jsonl")):
            try:
                tag = date.fromisoformat(datei.stem.removeprefix(VORSILBE))
            except ValueError:
                continue
            if tag < grenze:
                datei.unlink()
                geloescht.append(datei)
        return geloescht
