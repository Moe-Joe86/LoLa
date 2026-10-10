"""Startet LoLa wie `lola_start start`, aber mit zusätzlichen Schaltern für speech-to-speech (nur für Proben am
Roboter, z. B. die Stimme). Stoppen wie immer mit `lola_start stop`.

Aufruf: uv run python tests/a5/starte_stufe.py --qwen3_tts_xvec_only
Mit LOLA_STIMME=<Name> in der Umgebung lässt sich dazu eine andere Stimmdatei wählen.
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
    if "--qwen3_tts_xvec_only" in SCHALTER:  # verträgt sich nicht mit den gespeicherten Tonschritten (.rvq)
        stelle = befehl.index("--qwen3_tts_ref_rvq")
        befehl = befehl[:stelle] + befehl[stelle + 2 :]
    return alle | {"sprachkette": (befehl + SCHALTER, adresse, umgebung)}


lola_start.befehle = befehle_mit_schaltern
print(f"Zusätzliche Schalter für speech-to-speech: {SCHALTER or 'keine'}")
sys.exit(lola_start.starte(lola_start.einstellungen()))
