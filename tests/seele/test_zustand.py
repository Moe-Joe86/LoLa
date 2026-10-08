import pytest

from seele.charakter import charakter_laden
from seele.erklaer_log import ErklaerLog
from seele.zustand import RUHE_ERREGUNG, Zustand, aendern, grundzustand
from tests.attrappen.uhr import FesteUhr


@pytest.fixture
def uhr():
    return FesteUhr()


@pytest.fixture
def log(uhr):
    return ErklaerLog(uhr)


def test_grundzustand_folgt_der_grundstimmung(log):
    zustand = grundzustand(charakter_laden(), log)
    assert zustand.valenz == pytest.approx(0.3)
    assert zustand.erregung == RUHE_ERREGUNG


def test_start_steht_im_log(log, uhr):
    grundzustand(charakter_laden(), log)
    assert [(e.groesse, e.alt, e.ausloeser) for e in log.eintraege] == [
        ("valenz", None, "Start aus dem Charakter"),
        ("erregung", None, "Start aus dem Charakter"),
    ]
    assert all(e.zeit == uhr.zeit for e in log.eintraege)


def test_aenderung_mit_zeit_ausloeser_alt_und_neu(log, uhr):
    uhr.vorstellen(5)
    neu = aendern(Zustand(0.3, 0.3), log, "Test: Lob", valenz=0.5)
    assert neu == Zustand(0.5, 0.3)
    eintrag = log.eintraege[-1]
    assert (eintrag.zeit, eintrag.ausloeser, eintrag.groesse, eintrag.alt, eintrag.neu) == (
        uhr.zeit, "Test: Lob", "valenz", 0.3, 0.5)


def test_unveraenderter_wert_kommt_nicht_ins_log(log):
    aendern(Zustand(0.3, 0.3), log, "Test", valenz=0.3, erregung=0.6)
    assert [e.groesse for e in log.eintraege] == ["erregung"]


def test_werte_werden_auf_den_bereich_begrenzt(log):
    neu = aendern(Zustand(0.3, 0.3), log, "Test", valenz=-3.0, erregung=1.7)
    assert neu == Zustand(-1.0, 1.0)
    assert [e.neu for e in log.eintraege] == [-1.0, 1.0]


def test_alter_zustand_bleibt_unveraendert(log):
    alt = Zustand(0.3, 0.3)
    aendern(alt, log, "Test", valenz=0.9)
    assert alt == Zustand(0.3, 0.3)


def test_unbekannte_groesse_wird_abgelehnt(log):
    with pytest.raises(ValueError, match="unbekannte Zustandsgrößen: akku"):
        aendern(Zustand(0.3, 0.3), log, "Test", akku=0.5)
    assert log.eintraege == []


def test_aenderung_ohne_ausloeser_wird_abgelehnt(log):
    with pytest.raises(ValueError, match="Auslöser"):
        aendern(Zustand(0.3, 0.3), log, "", valenz=0.5)
