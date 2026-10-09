import json

from seele.charakter import charakter_laden
from seele.erklaer_log import ErklaerLog
from seele.zustand import aendern, grundzustand
from tests.attrappen.uhr import FesteUhr


def test_ohne_datei_bleibt_alles_im_speicher(tmp_path):
    log = ErklaerLog(FesteUhr())
    log.schreiben("Test", "valenz", None, 0.3)
    assert len(log.eintraege) == 1
    assert list(tmp_path.iterdir()) == []


def test_jeder_eintrag_wird_eine_zeile_json(tmp_path):
    datei = tmp_path / "daten" / "erklaer-log.jsonl"
    log = ErklaerLog(FesteUhr(), datei)
    zustand = grundzustand(charakter_laden(), log)
    aendern(zustand, log, "jemand lobt Lola überschwänglich", valenz=0.8)
    zeilen = [json.loads(zeile) for zeile in datei.read_text(encoding="utf-8").splitlines()]
    assert len(zeilen) == len(log.eintraege) == 3
    assert zeilen[0] == {
        "zeit": "2026-10-08T09:00:00+00:00",
        "ausloeser": "Start aus dem Charakter",
        "groesse": "valenz",
        "alt": None,
        "neu": zeilen[0]["neu"],
    }
    assert zeilen[2]["ausloeser"] == "jemand lobt Lola überschwänglich"
    assert (zeilen[2]["groesse"], zeilen[2]["neu"]) == ("valenz", 0.8)


def test_zweites_log_haengt_an_dieselbe_datei_an(tmp_path):
    datei = tmp_path / "erklaer-log.jsonl"
    ErklaerLog(FesteUhr(), datei).schreiben("eins", "valenz", 0.0, 0.1)
    ErklaerLog(FesteUhr(), datei).schreiben("zwei", "valenz", 0.1, 0.2)
    assert [json.loads(z)["ausloeser"] for z in datei.read_text(encoding="utf-8").splitlines()] == ["eins", "zwei"]
