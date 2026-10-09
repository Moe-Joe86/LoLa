import http.server
import json
import subprocess
import sys
import threading
import tomllib
import urllib.request
from pathlib import Path

import pytest

from dienste import lola_start


def werte(tmp_path):
    return lola_start.STANDARD | {"LOLA_LAUFZEIT": str(tmp_path)}


def test_einstellungen_env_datei_schlaegt_standard(tmp_path, monkeypatch):
    for name in lola_start.STANDARD:
        monkeypatch.delenv(name, raising=False)
    datei = tmp_path / ".env"
    datei.write_text("# Kommentar\nLOLA_STIMME = andere\nUNBEKANNT=1\n", encoding="utf-8")
    gelesen = lola_start.einstellungen(datei)
    assert gelesen["LOLA_STIMME"] == "andere"
    assert gelesen["LOLA_SPRACHMODELL"] == lola_start.STANDARD["LOLA_SPRACHMODELL"]
    assert "UNBEKANNT" not in gelesen


def test_einstellungen_umgebung_schlaegt_env_datei(tmp_path, monkeypatch):
    datei = tmp_path / ".env"
    datei.write_text("LOLA_STIMME=andere\n", encoding="utf-8")
    monkeypatch.setenv("LOLA_STIMME", "dritte")
    assert lola_start.einstellungen(datei)["LOLA_STIMME"] == "dritte"


def test_sprachmodell_lauscht_nur_lokal_sprachkette_im_netz(tmp_path):
    befehle = lola_start.befehle(werte(tmp_path))
    llama, kette = befehle["sprachmodell"][0], befehle["sprachkette"][0]
    assert llama[llama.index("--host") + 1] == "127.0.0.1"
    assert kette[kette.index("--host") + 1] == "0.0.0.0"
    assert kette[kette.index("--stream_batch_sentences") + 1] == "1"


def test_stimmdaten_kommen_nur_aus_dem_stimmen_ordner(tmp_path):
    (tmp_path / "stimmen").mkdir()
    (tmp_path / "stimmen" / "transkript.txt").write_text("Der Wortlaut.\n", encoding="utf-8")
    kette = lola_start.befehle(werte(tmp_path))["sprachkette"][0]
    stimmen = str(tmp_path / "stimmen")
    assert kette[kette.index("--qwen3_tts_ref_cache_dir") + 1] == stimmen
    assert kette[kette.index("--qwen3_tts_ref_spk") + 1] == f"{stimmen}/frau_0.6B-Base_Q8_0.spk"
    assert kette[kette.index("--qwen3_tts_ref_text") + 1] == "Der Wortlaut."


def test_stoppe_beendet_gestarteten_prozess(tmp_path, monkeypatch):
    monkeypatch.setattr(lola_start.time, "sleep", lambda _: None)  # der Test erntet den Prozess erst danach
    lauf = tmp_path / "lauf"
    lauf.mkdir()
    befehl = [sys.executable, "-c", "import time; time.sleep(60)"]
    prozess = subprocess.Popen(befehl)
    (lauf / "sprachmodell.pid").write_text(f"{prozess.pid}\n{lola_start._kennung(befehl)}", encoding="utf-8")
    assert lola_start.stoppe(werte(tmp_path)) == 0
    assert prozess.wait(timeout=5) is not None
    assert not (lauf / "sprachmodell.pid").exists()


def test_stoppe_laesst_fremden_prozess_in_ruhe(tmp_path):
    lauf = tmp_path / "lauf"
    lauf.mkdir()
    fremd = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    kennung = lola_start._kennung(["/anderes/programm", "serve"])
    (lauf / "sprachmodell.pid").write_text(f"{fremd.pid}\n{kennung}", encoding="utf-8")
    lola_start.stoppe(werte(tmp_path))
    assert fremd.poll() is None
    fremd.kill()
    fremd.wait()


class Daemon(http.server.BaseHTTPRequestHandler):
    """Attrappe des Reachy-Daemons: merkt sich alle Aufrufe und antwortet aus einer Tabelle."""

    aufrufe: list = []
    antworten: dict = {}

    def _antworte(self):
        laenge = int(self.headers.get("Content-Length") or 0)
        rumpf = json.loads(self.rfile.read(laenge)) if laenge else None
        Daemon.aufrufe.append((self.command, self.path, rumpf))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(Daemon.antworten.get(self.path, {})).encode())

    do_GET = do_POST = _antworte

    def log_message(self, *args):
        pass


@pytest.fixture
def daemon(tmp_path, monkeypatch):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Daemon)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    Daemon.aufrufe = []
    Daemon.antworten = {
        "/api/daemon/status": {"state": "running"},
        "/api/apps/current-app-status": None,
        "/api/audio/config/apply": {"applied": True},
        "/api/move/running": [],
        "/api/audio/config/parameter/PP_NLATTENONOFF": {"values": [0]},
    }
    echtes_oeffnen = urllib.request.urlopen

    def umgeleitet(anfrage, timeout):
        anfrage.full_url = anfrage.full_url.replace("reachy-mini.local:8000", f"127.0.0.1:{server.server_port}")
        return echtes_oeffnen(anfrage, timeout=timeout)

    monkeypatch.setattr(lola_start.urllib.request, "urlopen", umgeleitet)
    monkeypatch.setattr(lola_start.time, "sleep", lambda _: None)
    yield werte(tmp_path)
    server.shutdown()


def test_app_spricht_lokal_mit_sprache_auto_und_unserem_profil(tmp_path):
    befehl, _, umgebung = lola_start.befehle(werte(tmp_path))["app"]
    assert befehl[0].endswith("app-venv/bin/reachy-mini-conversation-app")
    assert umgebung["HF_REALTIME_CONNECTION_MODE"] == "local"
    assert umgebung["HF_REALTIME_WS_URL"] == "ws://127.0.0.1:8765/v1/realtime"
    assert umgebung["REALTIME_TRANSCRIPTION_LANGUAGE"] == "auto"
    profil = Path(umgebung["REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY"]) / umgebung["REACHY_MINI_CUSTOM_PROFILE"]
    _, kopf, text = (profil / "profile.md").read_text(encoding="utf-8").split("+++", 2)
    assert tomllib.loads(kopf)["schema_version"] == 1
    assert "Du bist LoLa" in text


def test_reachy_bereit_setzt_die_mikrofon_werte(daemon):
    assert lola_start.reachy_bereit(daemon) is True
    methode, pfad, rumpf = Daemon.aufrufe[-3]
    assert (methode, pfad) == ("POST", "/api/audio/config/apply")
    assert {"name": "PP_AGCMAXGAIN", "values": [3.0]} in rumpf["config"]
    assert len(rumpf["config"]) == 6
    assert all(isinstance(zahl, float) for paar in rumpf["config"] for zahl in paar["values"])


def test_reachy_bereit_setzt_die_lautstaerke_aus_den_einstellungen(daemon):
    assert lola_start.reachy_bereit(daemon | {"LOLA_LAUTSTAERKE": "80"}) is True
    assert ("POST", "/api/volume/set", {"volume": 80}) in Daemon.aufrufe


def test_sprachkette_startet_ueber_unser_startprogramm_mit_den_entschiedenen_schaltern(tmp_path):
    kette = lola_start.befehle(werte(tmp_path))["sprachkette"][0]
    assert kette[0].endswith("s2s-venv/bin/python")
    assert Path(kette[1]) == lola_start.REPO / "dienste" / "sprachkette_start.py" and Path(kette[1]).exists()
    assert kette[2] == "serve"
    assert "--no_enable_live_transcription" in kette
    assert kette[kette.index("--min_speech_ms") + 1] == "192"
    assert kette[kette.index("--qwen3_tts_max_new_tokens") + 1] == "190"
    assert "--vad" not in kette and "--speculative_reopen_ms" not in kette  # Silero und 800 ms: Standard


def test_reachy_bereit_warnt_wenn_der_ganzzahl_wert_abweicht(daemon, capsys):
    Daemon.antworten["/api/audio/config/parameter/PP_NLATTENONOFF"] = {"values": [1]}
    assert lola_start.reachy_bereit(daemon) is True
    assert "PP_NLATTENONOFF" in capsys.readouterr().out


def test_reachy_bereit_startet_nicht_neben_einer_app_auf_dem_reachy(daemon):
    Daemon.antworten["/api/apps/current-app-status"] = {"state": "running"}
    assert lola_start.reachy_bereit(daemon) is False
    assert all(methode == "GET" for methode, _, _ in Daemon.aufrufe)


def test_reachy_bereit_meldet_ausgeschalteten_reachy(tmp_path, monkeypatch):
    def keine_antwort(anfrage, timeout):
        raise OSError

    monkeypatch.setattr(lola_start.urllib.request, "urlopen", keine_antwort)
    assert lola_start.reachy_bereit(werte(tmp_path)) is False


def test_stoppe_legt_den_reachy_nach_der_app_schlafen(daemon):
    lauf = Path(daemon["LOLA_LAUFZEIT"]) / "lauf"
    lauf.mkdir()
    befehl = [sys.executable, "-c", "import time; time.sleep(60)"]
    prozess = subprocess.Popen(befehl)
    (lauf / "app.pid").write_text(f"{prozess.pid}\n{lola_start._kennung(befehl)}", encoding="utf-8")
    lola_start.stoppe(daemon)
    assert prozess.wait(timeout=5) is not None
    gesendet = [pfad for methode, pfad, _ in Daemon.aufrufe if methode == "POST"]
    assert gesendet == ["/api/move/play/goto_sleep", "/api/motors/set_mode/disabled"]


def test_stoppe_ohne_app_laesst_den_reachy_in_ruhe(daemon):
    (Path(daemon["LOLA_LAUFZEIT"]) / "lauf").mkdir()
    lola_start.stoppe(daemon)
    assert Daemon.aufrufe == []


def test_sprachkette_fragt_den_vermittler_und_der_vermittler_das_sprachmodell(tmp_path):
    befehle = lola_start.befehle(werte(tmp_path))
    assert list(befehle) == ["sprachmodell", "vermittler", "sprachkette", "app"]  # Reihenfolge des Starts
    kette = befehle["sprachkette"][0]
    assert kette[kette.index("--responses_api_base_url") + 1] == "http://127.0.0.1:8091/v1"
    vermittler, gesund, umgebung = befehle["vermittler"]
    assert vermittler[1:] == ["-m", "vermittler.proxy", "8091", "8090"]
    assert gesund == "http://127.0.0.1:8091/health"
    assert umgebung == {"LOLA_ANFRAGE_LOG_TAGE": "7"}


def test_kette_startet_keine_app_und_fasst_den_reachy_nicht_an(daemon, monkeypatch):
    monkeypatch.setattr(lola_start, "_antwortet", lambda adresse: True)  # alle Programme „laufen schon“
    assert lola_start.starte(daemon, mit_app=False) == 0
    assert Daemon.aufrufe == []
