import json

import pytest

from tests.attrappen.uhr import FesteUhr
from vermittler.anfrage_log import AnfrageLog, frist_tage

TAG = 24 * 3600


def test_eintrag_landet_als_eine_zeile_in_der_tagesdatei(tmp_path):
    log = AnfrageLog(tmp_path / "daten", FesteUhr())
    datei = log.schreiben("Wie geht es dir, Lola?", "[Zustand] Du, LoLa, bist ruhig.", ["dance"], 12.34)
    assert datei.name == "anfragen-2026-10-08.jsonl"
    assert json.loads(datei.read_text(encoding="utf-8")) == {
        "zeit": "2026-10-08T09:00:00+00:00",
        "gesagt": "Wie geht es dir, Lola?",
        "bericht": "[Zustand] Du, LoLa, bist ruhig.",
        "entfernte_tools": ["dance"],
        "dauer_ms": 12.3,
    }


def test_mehrere_eintraege_am_selben_tag_in_derselben_datei(tmp_path):
    uhr = FesteUhr()
    log = AnfrageLog(tmp_path, uhr)
    log.schreiben("eins", "", [], 1)
    uhr.vorstellen(3600)
    datei = log.schreiben("zwei", "", [], 1)
    assert [json.loads(z)["gesagt"] for z in datei.read_text(encoding="utf-8").splitlines()] == ["eins", "zwei"]
    assert len(list(tmp_path.iterdir())) == 1


def test_nach_sieben_tagen_ist_gesagtes_geloescht(tmp_path):
    uhr = FesteUhr()
    log = AnfrageLog(tmp_path, uhr)
    alt = log.schreiben("Das soll verschwinden.", "", [], 1)
    uhr.vorstellen(7 * TAG)
    log.schreiben("Tag sieben", "", [], 1)
    assert alt.exists()  # genau sieben Tage alt: bleibt noch
    uhr.vorstellen(TAG)
    log.schreiben("Tag acht", "", [], 1)
    assert not alt.exists()
    namen = sorted(datei.name for datei in tmp_path.iterdir())
    assert namen == ["anfragen-2026-10-15.jsonl", "anfragen-2026-10-16.jsonl"]
    assert "verschwinden" not in "".join(datei.read_text(encoding="utf-8") for datei in tmp_path.iterdir())


def test_aufraeumen_meldet_geloeschte_und_laesst_fremde_dateien_stehen(tmp_path):
    uhr = FesteUhr()
    log = AnfrageLog(tmp_path, uhr, frist=2)
    alt = log.schreiben("alt", "", [], 1)
    (tmp_path / "erklaer-log.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "anfragen-kaputt.jsonl").write_text("{}\n", encoding="utf-8")
    uhr.vorstellen(3 * TAG)
    assert log.aufraeumen() == [alt]
    assert sorted(datei.name for datei in tmp_path.iterdir()) == ["anfragen-kaputt.jsonl", "erklaer-log.jsonl"]


def test_frist_kommt_aus_der_umgebung():
    assert frist_tage({}) == 7
    assert frist_tage({"LOLA_ANFRAGE_LOG_TAGE": "3"}) == 3


@pytest.mark.parametrize("wert", ["", "bald", "0", "-2", "1.5"])
def test_unbrauchbare_frist_faellt_auf_sieben_tage_zurueck(wert):
    assert frist_tage({"LOLA_ANFRAGE_LOG_TAGE": wert}) == 7
