import subprocess
import sys

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
    prozess = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)", str(tmp_path)])
    (lauf / "sprachmodell.pid").write_text(str(prozess.pid), encoding="utf-8")
    assert lola_start.stoppe(werte(tmp_path)) == 0
    assert prozess.wait(timeout=5) is not None
    assert not (lauf / "sprachmodell.pid").exists()


def test_stoppe_laesst_fremden_prozess_in_ruhe(tmp_path):
    lauf = tmp_path / "lauf"
    lauf.mkdir()
    fremd = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    (lauf / "sprachmodell.pid").write_text(str(fremd.pid), encoding="utf-8")
    lola_start.stoppe(werte(tmp_path))
    assert fremd.poll() is None
    fremd.kill()
    fremd.wait()
