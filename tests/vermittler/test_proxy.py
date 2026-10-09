import http.client
import json
import threading
import time

import pytest

from tests.attrappen.llama import STUECKE, LlamaAttrappe
from tests.attrappen.uhr import FesteUhr
from tests.vermittler.test_anfrage import BERICHT, anfrage, nachricht, roh
from vermittler.anfrage_log import AnfrageLog
from vermittler.proxy import Einstellung, baue_server


class Aufbau:
    def __init__(self, tmp_path, llama: LlamaAttrappe, gesperrt: frozenset[str] = frozenset()) -> None:
        self.llama = llama
        self.ordner = tmp_path / "daten"
        self.uhr = FesteUhr()
        log = AnfrageLog(self.ordner, self.uhr)
        einstellung = Einstellung(("127.0.0.1", llama.port), lambda: BERICHT, log, lambda: gesperrt)
        self.server = baue_server(0, einstellung)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def verbinde(self) -> http.client.HTTPConnection:
        return http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=5)

    def sende(self, koerper: bytes, pfad: str = "/v1/responses") -> http.client.HTTPResponse:
        verbindung = self.verbinde()
        verbindung.request("POST", pfad, body=koerper, headers={"Content-Type": "application/json", "X-Test": "1"})
        return verbindung.getresponse()

    def log_zeilen(self) -> list[dict]:
        dateien = sorted(self.ordner.glob("anfragen-*.jsonl"))
        return [json.loads(zeile) for datei in dateien for zeile in datei.read_text(encoding="utf-8").splitlines()]


@pytest.fixture
def aufbau(tmp_path):
    aufbau = Aufbau(tmp_path, LlamaAttrappe())
    yield aufbau
    aufbau.server.shutdown()
    aufbau.llama.shutdown()


def warte_auf(bedingung, dauer: float = 2.0) -> bool:
    ende = time.monotonic() + dauer
    while time.monotonic() < ende:
        if bedingung():
            return True
        time.sleep(0.01)
    return False


def test_aufwaermen_geht_byte_gleich_durch_und_die_antwort_kommt_unveraendert(aufbau):
    aufwaermen = roh({"model": "qwen3", "input": [nachricht("system", "x"), nachricht("user", "Hello")]})
    antwort = aufbau.sende(aufwaermen)
    assert (antwort.status, antwort.getheader("X-Attrappe")) == (200, "ja")
    assert json.loads(antwort.read()) == {"output_text": "".join(STUECKE)}
    _, pfad, kopf, koerper = aufbau.llama.anfragen[0]
    assert (pfad, koerper, kopf["X-Test"]) == ("/v1/responses", aufwaermen, "1")
    assert aufbau.log_zeilen() == []  # kein Gespräch, also kein Eintrag


def test_gespraech_bekommt_den_bericht_vor_dem_letzten_nutzersatz(aufbau):
    vorher = anfrage()
    antwort = aufbau.sende(roh(vorher))
    text = antwort.read().decode()
    assert [json.loads(z[6:])["delta"] for z in text.splitlines() if z.startswith("data: ")] == STUECKE
    angekommen = json.loads(aufbau.llama.anfragen[0][3])
    assert angekommen["input"][3] == nachricht("system", BERICHT)
    assert angekommen["input"][:3] + angekommen["input"][4:] == vorher["input"]
    assert angekommen["tools"] == vorher["tools"]


def test_strom_wird_stueck_fuer_stueck_weitergereicht(tmp_path):
    aufbau = Aufbau(tmp_path, LlamaAttrappe(pause=0.2))
    beginn = time.monotonic()
    antwort = aufbau.sende(roh(anfrage()))
    zeiten = []
    while antwort.read1(65536):
        zeiten.append(time.monotonic() - beginn)
    assert len(zeiten) >= len(STUECKE)
    assert zeiten[0] < 0.15  # das erste Stück kommt sofort, nicht erst am Ende des Stroms
    assert zeiten[-1] > 0.55


def test_andere_pfade_und_fehlerstatus_gehen_durch(aufbau):
    verbindung = aufbau.verbinde()
    verbindung.request("GET", "/health")
    antwort = verbindung.getresponse()
    assert (antwort.status, antwort.read()) == (200, b'{"status":"ok"}')
    assert aufbau.sende(b"{}", "/gibt/es/nicht").status == 404


def test_gesperrte_tools_fehlen_in_der_anfrage_und_stehen_im_log(tmp_path):
    aufbau = Aufbau(tmp_path, LlamaAttrappe(pause=0), gesperrt=frozenset({"dance", "move_head"}))
    aufbau.sende(roh(anfrage())).read()
    assert [tool["name"] for tool in json.loads(aufbau.llama.anfragen[0][3])["tools"]] == ["camera"]
    assert warte_auf(lambda: len(aufbau.log_zeilen()) == 1)
    assert aufbau.log_zeilen()[0]["entfernte_tools"] == ["dance", "move_head"]


def test_anfrage_log_bekommt_gesagtes_bericht_und_kennzeichen(tmp_path):
    aufbau = Aufbau(tmp_path, LlamaAttrappe(pause=0))
    for nummer, satz in enumerate(("Wie geht", "Wie geht es dir?", "Tanz bitte."), 1):
        koerper = anfrage()
        koerper["input"][-1] = nachricht("user", satz)
        aufbau.sende(roh(koerper)).read()
        assert warte_auf(lambda anzahl=nummer: len(aufbau.log_zeilen()) == anzahl)
    zeilen = aufbau.log_zeilen()
    assert [zeile["wiederholt"] for zeile in zeilen] == [False, True, False]
    assert all(zeile["bericht"] == BERICHT and not zeile["abgebrochen"] for zeile in zeilen)
    assert all(zeile["dauer_ms"] >= 0 for zeile in zeilen)


def test_abbruch_mitten_im_strom_erreicht_llama_sofort(tmp_path):
    aufbau = Aufbau(tmp_path, LlamaAttrappe(pause=0.5))
    antwort = aufbau.sende(roh(anfrage()))
    assert antwort.read1(65536)
    antwort.close()
    assert warte_auf(lambda: aufbau.llama.abbruch_bemerkt_nach is not None, 1.0)
    assert aufbau.llama.abbruch_bemerkt_nach < 0.5  # vor dem zweiten Stück
    assert warte_auf(lambda: len(aufbau.log_zeilen()) == 1)
    assert aufbau.log_zeilen()[0]["abgebrochen"] is True


def test_abbruch_vor_dem_ersten_wort_erreicht_llama_sofort(tmp_path):
    aufbau = Aufbau(tmp_path, LlamaAttrappe(vorlauf=3.0))
    verbindung = aufbau.verbinde()
    verbindung.request("POST", "/v1/responses", body=roh(anfrage()))
    time.sleep(0.2)
    verbindung.close()
    assert warte_auf(lambda: aufbau.llama.abbruch_bemerkt_nach is not None, 1.5)
    assert aufbau.llama.abbruch_bemerkt_nach < 1.0  # weit vor dem ersten Stück nach 3 s
    assert warte_auf(lambda: len(aufbau.log_zeilen()) == 1)
    assert aufbau.log_zeilen()[0]["abgebrochen"] is True


def test_nach_einem_abbruch_laeuft_die_naechste_anfrage_normal(tmp_path):
    aufbau = Aufbau(tmp_path, LlamaAttrappe(pause=0.05))
    abgebrochen = aufbau.sende(roh(anfrage()))
    abgebrochen.read1(10)
    abgebrochen.close()
    assert b"LoLa." in aufbau.sende(roh(anfrage())).read()


def test_llama_nicht_erreichbar_gibt_502(tmp_path):
    aufbau = Aufbau(tmp_path, LlamaAttrappe())
    aufbau.llama.shutdown()
    aufbau.llama.server_close()
    antwort = aufbau.sende(roh(anfrage()))
    assert antwort.status == 502
    assert b"llama.cpp" in antwort.read()


def test_beim_start_werden_alte_anfrage_logs_weggeraeumt(tmp_path):
    ordner = tmp_path / "daten"
    ordner.mkdir()
    alt = ordner / "anfragen-2026-09-20.jsonl"
    neu = ordner / "anfragen-2026-10-05.jsonl"
    for datei in (alt, neu):
        datei.write_text("{}\n", encoding="utf-8")
    Aufbau(tmp_path, LlamaAttrappe())
    assert (alt.exists(), neu.exists()) == (False, True)
