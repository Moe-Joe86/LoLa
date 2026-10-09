"""Baut künstliche Aufnahmen mit Denkpause: sucht in einer A1-Aufnahme die leiseste Stelle nahe der Mitte
und fügt dort Stille ein. Ergebnis lokal in ~/lola-laufzeit/messung/pause/aufnahmen/.

Aufruf (mit der Umgebung von speech-to-speech, braucht numpy): python pause_aufnahmen.py
"""

import wave
from pathlib import Path

import numpy as np

QUELLE = Path.home() / "lola-laufzeit/messung/aufnahmen-synth"
ZIEL = Path.home() / "lola-laufzeit/messung/pause/aufnahmen"
SAETZE = (8, 9, 11, 12, 16, 17, 18, 19)
PAUSEN_MS = (300, 500, 700)
RATE = 16000
FENSTER = 480  # 30 ms


def leiseste_stelle(ton: np.ndarray) -> int:
    """Mitte des leisesten 30-ms-Fensters zwischen 30 und 70 Prozent der Aufnahme."""
    von, bis = int(len(ton) * 0.3), int(len(ton) * 0.7)
    stellen = range(von, bis - FENSTER, 80)
    laut = [float(np.abs(ton[s : s + FENSTER].astype(np.int32)).mean()) for s in stellen]
    return stellen[int(np.argmin(laut))] + FENSTER // 2


def main() -> None:
    ZIEL.mkdir(parents=True, exist_ok=True)
    for nummer in SAETZE:
        with wave.open(str(QUELLE / f"satz_{nummer:02}.wav")) as datei:
            ton = np.frombuffer(datei.readframes(datei.getnframes()), dtype=np.int16)
        stelle = leiseste_stelle(ton)
        dort = float(np.abs(ton[stelle - 240 : stelle + 240].astype(np.int32)).mean())
        print(
            f"Satz {nummer:2}: Schnitt bei {stelle / RATE:.2f} s von {len(ton) / RATE:.2f} s, "
            f"Pegel dort {dort:.0f}, im Mittel {np.abs(ton.astype(np.int32)).mean():.0f}"
        )
        for pause in PAUSEN_MS:
            neu = np.concatenate([ton[:stelle], np.zeros(RATE * pause // 1000, dtype=np.int16), ton[stelle:]])
            with wave.open(str(ZIEL / f"satz_{nummer:02}_pause_{pause}.wav"), "wb") as datei:
                datei.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
                datei.writeframes(neu.tobytes())
        (ZIEL / f"satz_{nummer:02}.schnitt").write_text(str(stelle), encoding="utf-8")


main()
