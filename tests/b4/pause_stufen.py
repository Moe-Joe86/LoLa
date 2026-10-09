"""Fährt die Stufen der Pausenerkennung: tauscht je Stufe nur die Sprachkette gegen eine mit anderen
Schaltern aus und lässt `pause_reihe.py` messen. Vorher muss `lola_start kette` laufen.

Aufruf: python3 pause_stufen.py [kurz] <stufe> [<stufe> ...]   (ohne Stufe: alle)
Danach `lola_start stop`; das beendet auch die zuletzt gestartete Sprachkette.
"""

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dienste import lola_start  # noqa: E402

STUFEN = {
    "standard": [],
    "standard2": [],  # Wiederholung, zeigt die Streuung zwischen zwei gleichen Läufen
    "halt600": ["--speculative_reopen_ms", "600"],
    "halt400": ["--speculative_reopen_ms", "400"],
    "halt200": ["--speculative_reopen_ms", "200"],
    "halt1200": ["--speculative_reopen_ms", "1200"],
    "ohne-smart": ["--no_smart_turn"],
    "kurz256": ["--min_speech_ms", "256"],
    "kurz192": ["--min_speech_ms", "192"],
    "kurz128": ["--min_speech_ms", "128"],
    "schwelle04": ["--thresh", "0.4"],
    "naht300": ["--short_segment_merge_ms", "300"],
    "stille200": ["--min_silence_ms", "200"],
    "schwelle03-kurz256": ["--thresh", "0.3", "--min_speech_ms", "256"],
    "kurz256-halt600": ["--min_speech_ms", "256", "--speculative_reopen_ms", "600"],
    "kurz256-halt400": ["--min_speech_ms", "256", "--speculative_reopen_ms", "400"],
}
MESSUNG = Path.home() / "lola-laufzeit/messung/pause"


def beende(datei: Path) -> None:
    """Beendet die laufende Sprachkette wie `lola_start stop`: erst Strg+C, nach 10 s hart."""
    pid = int(datei.read_text(encoding="utf-8").split("\n")[0])
    try:
        os.kill(pid, signal.SIGINT)
        for _ in range(100):
            os.kill(pid, 0)
            time.sleep(0.1)
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def main() -> int:
    kurz = sys.argv[1:2] == ["kurz"]
    namen = sys.argv[2 if kurz else 1 :] or list(STUFEN)
    werte = lola_start.einstellungen()
    laufzeit = Path(werte["LOLA_LAUFZEIT"]).expanduser()
    befehl, adresse, umgebung = lola_start.befehle(werte)["sprachkette"]
    pid_datei = laufzeit / "lauf/sprachkette.pid"
    MESSUNG.mkdir(parents=True, exist_ok=True)
    for name in namen:
        beende(pid_datei)
        log_datei = laufzeit / "lauf/sprachkette.log"
        with open(log_datei, "w", encoding="utf-8") as log:
            prozess = subprocess.Popen(
                befehl + STUFEN[name],
                stdout=log,
                stderr=log,
                env=os.environ | umgebung,
                cwd=laufzeit / "app-daten",
                start_new_session=True,
            )
        pid_datei.write_text(f"{prozess.pid}\n{lola_start._kennung(befehl)}", encoding="utf-8")
        if not lola_start._warte(name, prozess, adresse):
            return 1
        print(time.strftime(f"%T Stufe {name}: Sprachkette läuft mit {STUFEN[name]}"), flush=True)
        python = str(laufzeit / "s2s-venv/bin/python")
        reihe = [python, str(Path(__file__).with_name("pause_reihe.py")), name + ("-kurz" if kurz else "")]
        subprocess.run(reihe + (["kurz"] if kurz else []), check=False)
        shutil.copy(log_datei, MESSUNG / f"{name}{'-kurz' if kurz else ''}.log")
    return 0


sys.exit(main())
