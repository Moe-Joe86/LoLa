"""A1: Nimmt die Testsätze nacheinander mit dem PC-Mikrofon auf (16 kHz, mono).

Die Aufnahmen sind privat und landen außerhalb des Repos.
Aufruf: python aufnehmen.py [--ab 1] [--ziel ORDNER] [--geraet pulse]
Das ALSA-Gerät "default" nimmt auf diesem PC keine 16 kHz an, deshalb läuft die Aufnahme über "pulse".
"""

import argparse
import queue
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

RATE = 16000
SAETZE = Path(__file__).with_name("testsaetze.txt")
ZIEL = Path.home() / "lola-laufzeit" / "messung" / "aufnahmen"


def nimm_auf(geraet: str) -> np.ndarray:
    """Nimmt auf, bis Enter gedrückt wird."""
    stuecke: queue.Queue[np.ndarray] = queue.Queue()
    with sd.InputStream(
        samplerate=RATE, channels=1, dtype="float32", device=geraet, callback=lambda d, *_: stuecke.put(d.copy())
    ):
        input("   ● Aufnahme läuft. Satz sprechen, dann Enter drücken … ")
    teile = []
    while not stuecke.empty():
        teile.append(stuecke.get())
    return np.concatenate(teile)[:, 0] if teile else np.zeros(0, dtype="float32")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ab", type=int, default=1, help="bei diesem Satz beginnen")
    parser.add_argument("--ziel", type=Path, default=ZIEL)
    parser.add_argument("--geraet", default="pulse", help="Aufnahmegerät von sounddevice")
    args = parser.parse_args()
    args.ziel.mkdir(parents=True, exist_ok=True)
    saetze = [z.strip() for z in SAETZE.read_text(encoding="utf-8").splitlines() if z.strip()]

    print(f"{len(saetze)} Sätze. Sprich normal, etwa einen halben Meter vom Mikrofon entfernt.")
    nummer = args.ab
    while nummer <= len(saetze):
        print(f"\nSatz {nummer} von {len(saetze)}:\n   „{saetze[nummer - 1]}“")
        input("   Enter drücken, wenn du bereit bist … ")
        ton = nimm_auf(args.geraet)
        pegel = float(np.abs(ton).max()) if ton.size else 0.0
        print(f"   {ton.size / RATE:.1f} s aufgenommen, lautester Pegel {pegel:.2f} (gut: 0.1 bis 0.9)")
        if input("   Enter = weiter, w = wiederholen: ").strip().lower() == "w":
            continue
        sf.write(args.ziel / f"satz_{nummer:02d}.wav", ton, RATE, subtype="PCM_16")
        nummer += 1
    print(f"\nFertig. Aufnahmen liegen in {args.ziel}")


if __name__ == "__main__":
    main()
