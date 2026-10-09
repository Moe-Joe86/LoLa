"""Startet und stoppt LoLa auf dem PC: llama.cpp, Vermittler, speech-to-speech und die Conversation App.

Aufruf: uv run python -m dienste.lola_start start | kette | stop   (kette: alles ausser der App)
llama.cpp, speech-to-speech und die App liegen ausserhalb des Repos im Laufzeit-Ordner und bleiben unveraendert.
Auf dem Reachy laeuft nur der Daemon; er wird ueber seine REST-Schnittstelle angesprochen.
"""

import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PORT_SPRACHMODELL = 8090
PORT_VERMITTLER = 8091
PORT_SPRACHKETTE = 8765
PORT_APP = 7860
WARTEZEIT_S = 180
REPO = Path(__file__).resolve().parent.parent
PROFILE = REPO / "charakter" / "profile"
# Mikrofon-Werte, die die Conversation App beim Start setzt, wenn sie auf dem Reachy laeuft (Stand 2e43e80).
# Mikrofon des Reachy: Werte wie in der Conversation App, nur die Höchstverstärkung ist 3 statt 10.
# Mit 10 regelt das Mikrofon in der Stille Motorbrummen hoch (ENTSCHEIDUNGEN, 9. Oktober 2026).
MIKROFON = {
    "PP_AGCMAXGAIN": [3.0],
    "PP_MIN_NS": [0.8],
    "PP_MIN_NN": [0.8],
    "PP_GAMMA_E": [0.5],
    "PP_GAMMA_ETAIL": [0.5],
    "PP_MGSCALE": [4.0, 1.0, 1.0],
}
# Diesen Ganzzahl-Wert nimmt die REST-Schnittstelle des Daemons 1.11.0 nicht an; er wird nur geprueft.
MIKROFON_NUR_PRUEFEN = ("PP_NLATTENONOFF", [0])
STANDARD = {
    "LOLA_LAUFZEIT": "~/lola-laufzeit",
    "LOLA_SPRACHMODELL": "modelle/Qwen3-8B-Q4_K_M.gguf",
    "LOLA_STIMME": "frau_0.6B-Base_Q8_0",
    "LOLA_REACHY": "reachy-mini.local",
    "LOLA_PROFIL": "lola_deutsch",
    "LOLA_ANFRAGE_LOG_TAGE": "7",
    "LOLA_LAUTSTAERKE": "100",
}
# Schalter für speech-to-speech, entschieden am Roboter (ENTSCHEIDUNGEN, 9. Oktober 2026).
# Rückhaltezeit (800 ms) und Smart Turn bleiben auf den Standardwerten von speech-to-speech.
SPRACHKETTE_SCHALTER = [
    "--no_enable_live_transcription",  # Teilerkennung beim Sprechen aus: nur für die Live-Anzeige nötig
    *("--min_speech_ms", "192"),  # Mindestlänge für Sprache; mit dem Standard 384 wird „Ja.“ verschluckt
    *("--qwen3_tts_max_new_tokens", "190"),  # Sprachausgabe je Satz höchstens rund 15 s
]


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


def befehle(werte: dict[str, str]) -> dict[str, tuple[list[str], str, dict[str, str]]]:
    """Baut je Programm Kommandozeile, Gesundheits-Adresse und eigene Umgebungsvariablen."""
    laufzeit = Path(werte["LOLA_LAUFZEIT"]).expanduser()
    stimmen = laufzeit / "stimmen"
    stimme = stimmen / werte["LOLA_STIMME"]
    wortlaut = stimmen / "transkript.txt"
    llama = [
        str(laufzeit / "llama.cpp/build/bin/llama-server"),
        *("-m", str(laufzeit / werte["LOLA_SPRACHMODELL"]), "-ngl", "999", "-c", "8192", "--parallel", "1"),
        *("--host", "127.0.0.1", "--port", str(PORT_SPRACHMODELL), "--jinja", "--no-webui", "--slots"),
    ]
    kette = [  # über unser Startprogramm, damit Parakeet nach dem Laden von Silero alle Kerne behält
        *(str(laufzeit / "s2s-venv/bin/python"), str(REPO / "dienste/sprachkette_start.py")),
        *("serve", "--host", "0.0.0.0", "--port", str(PORT_SPRACHKETTE)),
        *("--stt", "parakeet-tdt", "--parakeet_tdt_device", "cpu"),
        *("--llm_backend", "responses-api", "--model_name", "qwen3", "--responses_api_api_key", ""),
        *("--responses_api_base_url", f"http://127.0.0.1:{PORT_VERMITTLER}/v1"),
        *("--stream_batch_sentences", "1", "--log_transcripts"),
        *("--tts", "qwen3", "--qwen3_tts_model_name", "Qwen/Qwen3-TTS-12Hz-0.6B-Base"),
        *("--qwen3_tts_backend", "ggml", "--qwen3_tts_ggml_quantization", "Q8_0"),
        *("--qwen3_tts_ref_spk", f"{stimme}.spk", "--qwen3_tts_ref_rvq", f"{stimme}.rvq"),
        *("--qwen3_tts_ref_text", wortlaut.read_text(encoding="utf-8").strip() if wortlaut.exists() else ""),
        *("--qwen3_tts_ref_cache_dir", str(stimmen), "--qwen3_tts_language", "german"),
        *SPRACHKETTE_SCHALTER,
    ]
    kette_umgebung = {
        "HF_HOME": str(laufzeit / "hf-cache"),
        "NLTK_DATA": str(laufzeit / "nltk"),
        "OMP_NUM_THREADS": "6",
        "HF_HUB_OFFLINE": "1",
    }
    app_umgebung = {
        "HF_REALTIME_CONNECTION_MODE": "local",
        "HF_REALTIME_WS_URL": f"ws://127.0.0.1:{PORT_SPRACHKETTE}/v1/realtime",
        "REALTIME_TRANSCRIPTION_LANGUAGE": "auto",
        "REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY": str(PROFILE),
        "REACHY_MINI_CUSTOM_PROFILE": werte["LOLA_PROFIL"],
        "REACHY_MINI_MEMORY_ENABLED": "false",
        "REACHY_MINI_INSTANCE_PATH": str(laufzeit / "app-daten"),
    }
    app = [str(laufzeit / "app-venv/bin/reachy-mini-conversation-app"), "--ui"]
    vermittler = [sys.executable, "-m", "vermittler.proxy", str(PORT_VERMITTLER), str(PORT_SPRACHMODELL)]
    frist = {"LOLA_ANFRAGE_LOG_TAGE": werte["LOLA_ANFRAGE_LOG_TAGE"]}
    return {
        "sprachmodell": (llama, f"http://127.0.0.1:{PORT_SPRACHMODELL}/health", {}),
        "vermittler": (vermittler, f"http://127.0.0.1:{PORT_VERMITTLER}/health", frist),
        "sprachkette": (kette, f"http://127.0.0.1:{PORT_SPRACHKETTE}/v1/pool", kette_umgebung),
        "app": (app, f"http://127.0.0.1:{PORT_APP}/", app_umgebung),
    }


def reachy(werte: dict[str, str], pfad: str, daten: dict | None = None, senden: bool = False):
    """Fragt den Daemon des Reachy (GET) oder schickt ihm etwas (POST). Gibt None zurueck, wenn er nicht antwortet."""
    rumpf = json.dumps(daten).encode() if daten is not None else (b"" if senden else None)
    anfrage = urllib.request.Request(f"http://{werte['LOLA_REACHY']}:8000{pfad}", data=rumpf)
    anfrage.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(anfrage, timeout=10) as antwort:
            return json.loads(antwort.read() or b"{}")
    except (OSError, ValueError):
        return None


def reachy_bereit(werte: dict[str, str]) -> bool:
    """Prueft, ob der Daemon laeuft und keine andere App den Reachy belegt, setzt Mikrofon und Lautstaerke."""
    if (reachy(werte, "/api/daemon/status") or {}).get("state") != "running":
        print(f"Reachy ({werte['LOLA_REACHY']}) antwortet nicht. Ist er eingeschaltet?")
        return False
    if reachy(werte, "/api/apps/current-app-status") is not None:
        print("Auf dem Reachy läuft schon eine App. Bitte dort erst stoppen.")
        return False
    paare = [{"name": name, "values": werte_} for name, werte_ in MIKROFON.items()]
    if not (reachy(werte, "/api/audio/config/apply", {"config": paare}) or {}).get("applied"):
        print("Hinweis: Die Mikrofon-Werte ließen sich nicht setzen.")
    reachy(werte, "/api/volume/set", {"volume": int(werte["LOLA_LAUTSTAERKE"])})
    name, soll = MIKROFON_NUR_PRUEFEN
    if (reachy(werte, f"/api/audio/config/parameter/{name}") or {}).get("values") != soll:
        print(f"Hinweis: Mikrofon-Wert {name} steht nicht auf {soll[0]} und lässt sich von hier nicht setzen.")
    return True


def lege_schlafen(werte: dict[str, str]) -> None:
    """Legt den Reachy in die Schlafhaltung und schaltet die Motoren aus. Die App tut das beim Stoppen nicht."""
    if reachy(werte, "/api/move/play/goto_sleep", senden=True) is None:
        print("Reachy antwortet nicht, er wurde nicht schlafen gelegt.")
        return
    for _ in range(20):
        time.sleep(0.5)
        if not reachy(werte, "/api/move/running"):
            break
    reachy(werte, "/api/motors/set_mode/disabled", senden=True)
    print("Reachy: schläft, Motoren aus.")


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


def starte(werte: dict[str, str], mit_app: bool = True) -> int:
    """Startet die Programme nacheinander; die App erst, wenn der Reachy bereit ist."""
    laufzeit = Path(werte["LOLA_LAUFZEIT"]).expanduser()
    lauf = laufzeit / "lauf"
    lauf.mkdir(parents=True, exist_ok=True)
    (laufzeit / "app-daten").mkdir(exist_ok=True)
    for name, (befehl, adresse, eigene) in befehle(werte).items():
        if name == "app" and not mit_app:
            print("\nDie Sprachkette läuft. Die App wurde nicht gestartet, der Reachy bleibt, wie er ist.")
            return 0
        if _antwortet(adresse):
            print(f"{name}: läuft schon.")
            continue
        if name == "app" and not reachy_bereit(werte):
            print("Die Sprachkette läuft, die App wurde nicht gestartet.")
            return 1
        with open(lauf / f"{name}.log", "w", encoding="utf-8") as log:
            ort = REPO if name == "vermittler" else laufzeit / "app-daten"  # der Vermittler schreibt nach daten/
            prozess = subprocess.Popen(
                befehl, stdout=log, stderr=log, env=os.environ | eigene, cwd=ort, start_new_session=True
            )
        (lauf / f"{name}.pid").write_text(f"{prozess.pid}\n{_kennung(befehl)}", encoding="utf-8")
        print(f"{name}: startet …")
        if not _warte(name, prozess, adresse):
            print(f"Abbruch. Mehr steht in {lauf / f'{name}.log'}. Ich stoppe wieder alles.")
            stoppe(werte)
            return 1
        print(f"{name}: antwortet.")
    print(f"\nLoLa läuft und hört zu. Einstellungen der App: http://127.0.0.1:{PORT_APP}/")
    return 0


def _kennung(befehl: list[str]) -> str:
    """Anfang der Kommandozeile, so wie das Betriebssystem ihn fuehrt: daran erkennt `stoppe` das Programm."""
    return "\0".join(befehl[:3])


def stoppe(werte: dict[str, str]) -> int:
    """Beendet die Programme, die `starte` gestartet hat, die App zuerst. Danach schlaeft der Reachy."""
    lauf = Path(werte["LOLA_LAUFZEIT"]).expanduser() / "lauf"
    for datei in sorted(lauf.glob("*.pid")):
        nummer, _, kennung = datei.read_text(encoding="utf-8").partition("\n")
        pid = int(nummer)
        zeile = Path(f"/proc/{pid}/cmdline")
        fremd = zeile.exists() and kennung.encode() not in zeile.read_bytes()
        try:
            if not fremd:  # nach einem Neustart des PCs kann die Nummer einem anderen Programm gehoeren
                os.kill(pid, signal.SIGINT)  # wie Strg+C, damit jedes Programm sauber aufraeumt
                for _ in range(100):
                    os.kill(pid, 0)
                    time.sleep(0.1)
                os.kill(pid, getattr(signal, "SIGKILL", signal.SIGTERM))
        except ProcessLookupError:
            pass
        datei.unlink()
        print(f"{datei.stem}: gestoppt.")
        if datei.stem == "app":
            lege_schlafen(werte)
    return 0


def main() -> int:
    aktionen = {"start": starte, "kette": lambda werte: starte(werte, mit_app=False), "stop": stoppe}
    aktion = aktionen.get(sys.argv[1] if len(sys.argv) > 1 else "")
    if aktion is None:
        print("Aufruf: uv run python -m dienste.lola_start start | kette | stop")
        return 2
    return aktion(einstellungen())


if __name__ == "__main__":
    sys.exit(main())
