"""A1: Misst Spracherkennung auf der CPU: Zeit pro Satz und Wortfehler bei den Testsätzen.

Ohne Argumente: alle Kombinationen nacheinander, jede in einem eigenen Prozess mit fester Thread-Zahl
(OMP_NUM_THREADS, so würde es auch in der Sprachkette eingestellt). Aufrufe wie im Handler von
speech-to-speech (Commit 8024ccf): faster-whisper mit beam_size=1, Parakeet über nano-parakeet.
Aufruf: python stt_messen.py [--aufnahmen ORDNER] [--laeufe 3]
"""

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

SAETZE = Path(__file__).with_name("testsaetze.txt")
AUFNAHMEN = Path.home() / "lola-laufzeit" / "messung" / "aufnahmen"
KOMBINATIONEN = [
    ("parakeet", "nvidia/parakeet-tdt-0.6b-v3"),
    ("whisper", "large-v3-turbo"),
    ("whisper", "medium"),
    ("whisper", "small"),
]
THREADS = [4, 6, 8]


def woerter(text: str) -> list[str]:
    return re.sub(r"[^\wäöüß ]", " ", text.lower()).split()


def wortfehler(soll: list[str], ist: list[str]) -> int:
    """Kleinste Zahl an Ersetzungen, Einfügungen und Auslassungen (Levenshtein auf Wörtern)."""
    zeile = list(range(len(ist) + 1))
    for i, wort in enumerate(soll, 1):
        neu = [i]
        for j, anderes in enumerate(ist, 1):
            neu.append(min(zeile[j] + 1, neu[j - 1] + 1, zeile[j - 1] + (wort != anderes)))
        zeile = neu
    return zeile[-1]


def lade_erkenner(art: str, modell: str):
    """Gibt eine Funktion zurück, die ein Audio (16 kHz, float32) in Text umsetzt."""
    if art == "whisper":
        from faster_whisper import WhisperModel

        whisper = WhisperModel(modell, device="cpu", compute_type="int8")

        def erkenne(ton: np.ndarray) -> str:
            teile, _ = whisper.transcribe(
                ton, language="de", beam_size=1, max_new_tokens=128, without_timestamps=True, task="transcribe"
            )
            return " ".join(teil.text for teil in teile).strip()

        return erkenne
    from nano_parakeet import from_pretrained

    parakeet = from_pretrained(model_name=modell, device="cpu")
    return lambda ton: parakeet.transcribe(ton).strip()


def miss_eine(art: str, modell: str, aufnahmen: Path, laeufe: int) -> dict:
    saetze = [z.strip() for z in SAETZE.read_text(encoding="utf-8").splitlines() if z.strip()]
    start = time.perf_counter()
    erkenne = lade_erkenner(art, modell)
    erkenne(np.zeros(16000, dtype=np.float32))
    laden = time.perf_counter() - start
    zeilen, fehler_summe, wort_summe = [], 0, 0
    for nummer, soll in enumerate(saetze, 1):
        datei = aufnahmen / f"satz_{nummer:02d}.wav"
        if not datei.exists():
            continue
        ton, rate = sf.read(datei, dtype="float32")
        if rate != 16000:
            raise ValueError(f"{datei} hat {rate} Hz, erwartet 16000")
        zeiten, text = [], ""
        for _ in range(laeufe):
            beginn = time.perf_counter()
            text = erkenne(ton)
            zeiten.append(time.perf_counter() - beginn)
        fehler = wortfehler(woerter(soll), woerter(text))
        fehler_summe += fehler
        wort_summe += len(woerter(soll))
        zeit = round(statistics.median(zeiten), 3)
        zeilen.append({"nr": nummer, "audio_s": round(len(ton) / rate, 2), "zeit_s": zeit,
                       "fehler": fehler, "soll": soll, "ist": text})
    zeiten_alle = [z["zeit_s"] for z in zeilen]
    return {
        "art": art, "modell": modell, "threads": int(os.environ.get("OMP_NUM_THREADS", "0")),
        "laden_s": round(laden, 1), "saetze": len(zeilen),
        "zeit_mittel_s": round(statistics.mean(zeiten_alle), 3), "zeit_max_s": round(max(zeiten_alle), 3),
        "wortfehler": fehler_summe, "woerter": wort_summe,
        "wortfehlerrate": round(fehler_summe / wort_summe, 3),
        "saetze_mit_fehler": sum(1 for z in zeilen if z["fehler"]), "zeilen": zeilen,
    }


def miss_alle(aufnahmen: Path, laeufe: int, ziel: Path) -> None:
    ergebnisse = []
    for art, modell in KOMBINATIONEN:
        for threads in THREADS:
            umgebung = {**os.environ, "OMP_NUM_THREADS": str(threads)}
            befehl = [sys.executable, __file__, "--art", art, "--modell", modell,
                      "--aufnahmen", str(aufnahmen), "--laeufe", str(laeufe)]
            aus = subprocess.run(befehl, env=umgebung, capture_output=True, text=True, check=False).stdout
            zeile = next((z for z in aus.splitlines() if z.startswith("ERGEBNIS ")), None)
            if zeile is None:
                print(f"FEHLGESCHLAGEN: {art} {modell} {threads} Threads", flush=True)
                continue
            e = json.loads(zeile[9:])
            ergebnisse.append(e)
            print(f"{e['art']:9} {e['modell']:28} {threads} Threads: {e['zeit_mittel_s']:.3f} s im Mittel, "
                  f"{e['zeit_max_s']:.3f} s höchstens, {e['wortfehler']}/{e['woerter']} Wortfehler, "
                  f"{e['saetze_mit_fehler']} Sätze mit Fehler", flush=True)
    ziel.write_text(json.dumps(ergebnisse, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Einzelheiten in {ziel}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--art", choices=["whisper", "parakeet"])
    parser.add_argument("--modell")
    parser.add_argument("--aufnahmen", type=Path, default=AUFNAHMEN)
    parser.add_argument("--laeufe", type=int, default=3)
    parser.add_argument("--ziel", type=Path, default=AUFNAHMEN.parent / "stt-ergebnis.json")
    args = parser.parse_args()
    if args.art:
        ergebnis = miss_eine(args.art, args.modell, args.aufnahmen, args.laeufe)
        print("ERGEBNIS " + json.dumps(ergebnis, ensure_ascii=False))
    else:
        miss_alle(args.aufnahmen, args.laeufe, args.ziel)


if __name__ == "__main__":
    main()
