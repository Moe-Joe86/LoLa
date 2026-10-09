"""Startet LoLa wie `lola_start start`, aber mit zusätzlichen Schaltern für speech-to-speech (nur für die
Sitzung am Roboter, um Stufen der Pausenerkennung zu vergleichen). Stoppen wie immer mit `lola_start stop`.

Aufruf: uv run python tests/a4/starte_stufe.py --min_speech_ms 256 --speculative_reopen_ms 600
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dienste import lola_start  # noqa: E402

SCHALTER = sys.argv[1:]
_befehle = lola_start.befehle


def befehle_mit_schaltern(werte: dict[str, str]) -> dict:
    alle = _befehle(werte)
    befehl, adresse, umgebung = alle["sprachkette"]
    return alle | {"sprachkette": (befehl + SCHALTER, adresse, umgebung)}


lola_start.befehle = befehle_mit_schaltern
print(f"Zusätzliche Schalter für speech-to-speech: {SCHALTER or 'keine'}")
sys.exit(lola_start.starte(lola_start.einstellungen()))
