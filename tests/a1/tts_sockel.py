"""A1: Wo steckt der Grafikspeicher der Sprachausgabe, und geht sie auf der CPU?

Ruft qwentts.cpp direkt auf, weil faster-qwen3-tts den Puffer des Tonwandlers (codec_chunk_sec)
nicht durchreicht. Grafikspeicher immer als Wert des eigenen Prozesses, dazu die Gesamtbelegung vorher.
Aufruf: python tts_sockel.py [--cpu] [--puffer_s 24] [--ohne_fa] [--modell 0.6B-CustomVoice] [--quant Q8_0]
Threads auf der CPU über die Umgebung (OMP_NUM_THREADS) oder taskset.
"""

import argparse
import json
import os
import subprocess
import time

import numpy as np
from tts_messen import SAETZE, grafikspeicher_mib


def gesamt_mib() -> int:
    aus = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=False,
    ).stdout
    return int(aus.strip().splitlines()[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modell", default="0.6B-CustomVoice")
    parser.add_argument("--quant", default="Q8_0")
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--puffer_s", type=float, default=24.0, help="codec_chunk_sec beim Laden")
    parser.add_argument("--ohne_fa", action="store_true", help="Flash Attention aus")
    parser.add_argument("--protokoll", default="warning")
    args = parser.parse_args()
    if args.cpu:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        os.environ["GGML_BACKEND"] = "CPU"
    vorher = gesamt_mib()

    from qwentts_cpp import QwenTTS

    start = time.perf_counter()
    tts = QwenTTS.from_pretrained(
        f"Qwen/Qwen3-TTS-12Hz-{args.modell}", quant=args.quant, use_fa=not args.ohne_fa,
        codec_chunk_sec=args.puffer_s, log_level=args.protokoll,
    )
    laden = time.perf_counter() - start
    nach_laden = grafikspeicher_mib()

    def sprich(text: str) -> tuple[float, float, float]:
        beginn, erster, laenge, rate = time.perf_counter(), None, 0, 24000
        for stueck, stueck_rate in tts.stream(text=text, lang="german", speaker="aiden", codec_chunk_sec=0.96):
            rate = stueck_rate
            erster = erster or time.perf_counter() - beginn
            laenge += np.asarray(stueck).size
        return erster, time.perf_counter() - beginn, laenge / rate

    sprich("Hallo.")
    werte, spitze = [], grafikspeicher_mib()
    for satz in SAETZE:
        werte.append(sprich(satz))
        spitze = max(spitze, grafikspeicher_mib())
    print("ERGEBNIS " + json.dumps({
        "modell": args.modell, "quant": args.quant, "cpu": args.cpu, "threads": os.environ.get("OMP_NUM_THREADS"),
        "puffer_s": args.puffer_s, "flash_attention": not args.ohne_fa, "laden_s": round(laden, 1),
        "gpu_gesamt_vorher_mib": vorher, "vram_prozess_laden_mib": nach_laden, "vram_prozess_betrieb_mib": spitze,
        "erster_ton_mittel_s": round(float(np.mean([w[0] for w in werte])), 3),
        "erster_ton_max_s": round(max(w[0] for w in werte), 3),
        "rechenzeit_je_s_sprache": round(sum(w[1] for w in werte) / sum(w[2] for w in werte), 3),
    }))


if __name__ == "__main__":
    main()
