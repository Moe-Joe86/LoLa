"""Startet und stoppt die lokale Sprachkette auf dem PC: llama.cpp und speech-to-speech.

Aufruf: uv run python -m dienste.lola_start start | stop
Beide Programme liegen ausserhalb des Repos im Laufzeit-Ordner und bleiben unveraendert.
"""

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PORT_SPRACHMODELL = 8090
PORT_SPRACHKETTE = 8765
WARTEZEIT_S = 180
STANDARD = {
    "LOLA_LAUFZEIT": "~/lola-laufzeit",
    "LOLA_SPRACHMODELL": "modelle/Qwen3-8B-Q4_K_M.gguf",
    "LOLA_STIMME": "frau_0.6B-Base_Q8_0",
}


def einstellungen(env_datei: Path = Path(".env")) -> dict[str, str]:
    """Liest die Einstellungen: Standard, darueber `.env`, darueber die Umgebung."""
    werte = dict(STANDARD)
    if env_datei.exists():
        for zeile in env_datei.read_text(encoding="utf-8").splitlines():
            name, trenner, wert = zeile.partition("=")
            if trenner and name.strip() in STANDARD:
                werte[name.strip()] = wert.strip()
    werte.update({name: os.environ[name] for name in STANDARD if name in os.environ})
    return werte


def befehle(werte: dict[str, str]) -> dict[str, tuple[list[str], str]]:
    """Baut je Programm die Kommandozeile und die Adresse, an der es sich gesund meldet."""
    laufzeit = Path(werte["LOLA_LAUFZEIT"]).expanduser()
    stimmen = laufzeit / "stimmen"
    stimme = stimmen / werte["LOLA_STIMME"]
    wortlaut = stimmen / "transkript.txt"
    llama = [
        str(laufzeit / "llama.cpp/build/bin/llama-server"),
        *("-m", str(laufzeit / werte["LOLA_SPRACHMODELL"]), "-ngl", "999", "-c", "8192", "--parallel", "1"),
        *("--host", "127.0.0.1", "--port", str(PORT_SPRACHMODELL), "--jinja", "--no-webui", "--slots"),
    ]
    kette = [
        str(laufzeit / "s2s-venv/bin/speech-to-speech"),
        *("serve", "--host", "0.0.0.0", "--port", str(PORT_SPRACHKETTE)),
        *("--stt", "parakeet-tdt", "--parakeet_tdt_device", "cpu"),
        *("--llm_backend", "responses-api", "--model_name", "qwen3", "--responses_api_api_key", ""),
        *("--responses_api_base_url", f"http://127.0.0.1:{PORT_SPRACHMODELL}/v1"),
        *("--stream_batch_sentences", "1", "--log_transcripts"),
        *("--tts", "qwen3", "--qwen3_tts_model_name", "Qwen/Qwen3-TTS-12Hz-0.6B-Base"),
        *("--qwen3_tts_backend", "ggml", "--qwen3_tts_ggml_quantization", "Q8_0"),
        *("--qwen3_tts_ref_spk", f"{stimme}.spk", "--qwen3_tts_ref_rvq", f"{stimme}.rvq"),
        *("--qwen3_tts_ref_text", wortlaut.read_text(encoding="utf-8").strip() if wortlaut.exists() else ""),
        *("--qwen3_tts_ref_cache_dir", str(stimmen), "--qwen3_tts_language", "german"),
    ]
    return {
        "sprachmodell": (llama, f"http://127.0.0.1:{PORT_SPRACHMODELL}/health"),
        "sprachkette": (kette, f"http://127.0.0.1:{PORT_SPRACHKETTE}/v1/pool"),
    }


def _antwortet(adresse: str) -> bool:
    try:
        with urllib.request.urlopen(adresse, timeout=2) as antwort:
            return antwort.status == 200
    except OSError:
        return False


def _warte(name: str, prozess: subprocess.Popen, adresse: str) -> bool:
    ende = time.monotonic() + WARTEZEIT_S
    while time.monotonic() < ende:
        if _antwortet(adresse):
            return True
        if prozess.poll() is not None:
            print(f"{name}: beendet sich beim Start (Code {prozess.returncode}).")
            return False
        time.sleep(1)
    print(f"{name}: antwortet nach {WARTEZEIT_S} s noch nicht.")
    return False


def starte(werte: dict[str, str]) -> int:
    """Startet beide Programme nacheinander und meldet die Adresse fuer die App."""
    laufzeit = Path(werte["LOLA_LAUFZEIT"]).expanduser()
    lauf = laufzeit / "lauf"
    lauf.mkdir(parents=True, exist_ok=True)
    umgebung = os.environ | {
        "HF_HOME": str(laufzeit / "hf-cache"),
        "NLTK_DATA": str(laufzeit / "nltk"),
        "OMP_NUM_THREADS": "6",
        "HF_HUB_OFFLINE": "1",
    }
    for name, (befehl, adresse) in befehle(werte).items():
        if _antwortet(adresse):
            print(f"{name}: läuft schon.")
            continue
        with open(lauf / f"{name}.log", "w", encoding="utf-8") as log:
            prozess = subprocess.Popen(befehl, stdout=log, stderr=log, env=umgebung, start_new_session=True)
        (lauf / f"{name}.pid").write_text(str(prozess.pid), encoding="utf-8")
        print(f"{name}: startet …")
        if not _warte(name, prozess, adresse):
            print(f"Abbruch. Mehr steht in {lauf / f'{name}.log'}. Ich stoppe wieder alles.")
            stoppe(werte)
            return 1
        print(f"{name}: antwortet.")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("192.0.2.1", 9))  # sendet nichts, zeigt nur die eigene Adresse im Heimnetz
        ip = s.getsockname()[0]
    print(f"\nLoLa läuft. In der App eintragen: Host {socket.gethostname()}.local, Port {PORT_SPRACHKETTE}.")
    print(f"Geht der Name nicht: Host {ip} (kann sich ändern, dann in der App anpassen).")
    return 0


def stoppe(werte: dict[str, str]) -> int:
    """Beendet die Programme, die `starte` gestartet hat."""
    lauf = Path(werte["LOLA_LAUFZEIT"]).expanduser() / "lauf"
    for datei in sorted(lauf.glob("*.pid"), reverse=True):
        pid = int(datei.read_text(encoding="utf-8"))
        kennung = Path(f"/proc/{pid}/cmdline")
        fremd = kennung.exists() and str(lauf.parent).encode() not in kennung.read_bytes()
        try:
            if not fremd:  # nach einem Neustart des PCs kann die Nummer einem anderen Programm gehoeren
                os.kill(pid, signal.SIGTERM)
                for _ in range(100):
                    os.kill(pid, 0)
                    time.sleep(0.1)
                os.kill(pid, getattr(signal, "SIGKILL", signal.SIGTERM))
        except ProcessLookupError:
            pass
        datei.unlink()
        print(f"{datei.stem}: gestoppt.")
    return 0


def main() -> int:
    aktion = {"start": starte, "stop": stoppe}.get(sys.argv[1] if len(sys.argv) > 1 else "")
    if aktion is None:
        print("Aufruf: uv run python -m dienste.lola_start start | stop")
        return 2
    return aktion(einstellungen())


if __name__ == "__main__":
    sys.exit(main())
