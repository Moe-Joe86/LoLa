"""A1: Misst eine Qwen3-TTS-Variante (GGML): Grafikspeicher, Zeit bis zum ersten Ton, WAV-Dateien.

Eine Variante pro Aufruf, damit der Grafikspeicher sauber gemessen wird.
Aufruf: python tts_messen.py --modell 1.7B-CustomVoice --quant Q4_K_M --sprecher Aiden
        python tts_messen.py --modell 1.7B-Base --quant Q4_K_M --ref_audio frau.wav --ref_text "..." --name frau
"""

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import soundfile as sf

SAETZE = [
    "Guten Morgen! Hast du gut geschlafen?",
    "Ja, gerne.",
    "Der Timer für zwölf Minuten läuft. Ich sage dir Bescheid, wenn die Nudeln fertig sind.",
    "Oh, das tut mir leid. Möchtest du mir erzählen, was passiert ist?",
    "Am Donnerstag um achtzehn Uhr hat Johanna Fußballtraining in Lübeck, und Frau Schneider holt sie ab.",
]
ZIEL = Path.home() / "lola-laufzeit" / "messung" / "tts"


def grafikspeicher_mib() -> int:
    """Grafikspeicher dieses Prozesses laut nvidia-smi, 0 wenn er dort nicht auftaucht."""
    aus = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=False,
    ).stdout
    for zeile in aus.splitlines():
        pid, mib = (teil.strip() for teil in zeile.split(","))
        if int(pid) == os.getpid():
            return int(mib)
    return 0


def strom(modell, args, text):
    """Liefert den passenden Audiostrom für feste Stimme oder Referenzstimme."""
    if args.ref_audio:
        return modell.generate_voice_clone_streaming(
            text=text, language="german", ref_audio=args.ref_audio, ref_text=args.ref_text
        )
    return modell.generate_custom_voice_streaming(text=text, speaker=args.sprecher, language="german")


def sprich(modell, args, text, datei: Path) -> dict:
    start = time.perf_counter()
    erster, stuecke, rate = None, [], 24000
    for stueck, stueck_rate, _ in strom(modell, args, text):
        rate = stueck_rate
        erster = erster or time.perf_counter() - start
        stuecke.append(np.asarray(stueck, dtype=np.float32).reshape(-1))
    gesamt = time.perf_counter() - start
    ton = np.concatenate(stuecke)
    sf.write(datei, ton, rate, subtype="PCM_16")
    return {"erster_ton_s": round(erster, 3), "gesamt_s": round(gesamt, 3), "audio_s": round(ton.size / rate, 2)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modell", required=True, help="z. B. 0.6B-CustomVoice, 1.7B-CustomVoice, 1.7B-Base")
    parser.add_argument("--quant", required=True)
    parser.add_argument("--sprecher", default="Aiden")
    parser.add_argument("--ref_audio")
    parser.add_argument("--ref_text", default="")
    parser.add_argument("--name", help="Name der Referenzstimme für den Dateinamen")
    parser.add_argument("--nur_satz", type=int, help="nur diesen Satz sprechen (1 bis 5)")
    args = parser.parse_args()

    from faster_qwen3_tts import FasterQwen3TTS

    start = time.perf_counter()
    modell = FasterQwen3TTS.from_pretrained(
        f"Qwen/Qwen3-TTS-12Hz-{args.modell}", device="cuda", backend="ggml", quant=args.quant
    )
    laden = time.perf_counter() - start
    stimme = args.name or args.sprecher
    ordner = ZIEL / f"{args.modell}_{args.quant}"
    ordner.mkdir(parents=True, exist_ok=True)

    ergebnis = {
        "modell": args.modell, "quant": args.quant, "stimme": stimme, "laden_s": round(laden, 2),
        "vram_nach_laden_mib": grafikspeicher_mib(),
        "sprecher_im_modell": list(modell.get_supported_speakers() or []) if not args.ref_audio else [],
    }
    sprich(modell, args, "Hallo.", ordner / "aufwaermen.wav")
    (ordner / "aufwaermen.wav").unlink()
    nummern = [args.nur_satz] if args.nur_satz else range(1, len(SAETZE) + 1)
    saetze, spitze = [], grafikspeicher_mib()
    for nummer in nummern:
        saetze.append(sprich(modell, args, SAETZE[nummer - 1], ordner / f"{stimme}_satz{nummer}.wav"))
        spitze = max(spitze, grafikspeicher_mib())
    ergebnis["vram_betrieb_mib"] = spitze
    ergebnis["saetze"] = saetze
    ergebnis["erster_ton_mittel_s"] = round(float(np.mean([s["erster_ton_s"] for s in saetze])), 3)
    print("ERGEBNIS " + json.dumps(ergebnis, ensure_ascii=False))


if __name__ == "__main__":
    main()
