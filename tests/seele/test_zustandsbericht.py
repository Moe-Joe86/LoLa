import pytest

from seele.charakter import charakter_laden, charakter_pruefen
from seele.erklaer_log import ErklaerLog
from seele.zustand import Zustand, grundzustand
from seele.zustandsbericht import zustandsbericht
from tests.attrappen.uhr import FesteUhr


def test_bericht_fuer_reachy_im_grundzustand():
    charakter = charakter_laden()
    bericht = zustandsbericht(charakter, grundzustand(charakter, ErklaerLog(FesteUhr())))
    assert bericht == (
        "Innerer Zustand (nicht vorlesen, nur danach handeln):\n"
        "- Du bist gut gelaunt und ruhig.\n"
        "- Deine Art: gesellig und neugierig.\n"
        "- Halte dich kurz, höchstens zwei Sätze."
    )


@pytest.mark.parametrize(("valenz", "laune"), [
    (-1.0, "bedrückt"),
    (-0.4, "etwas gedrückter Stimmung"),
    (0.0, "ausgeglichen"),
    (0.3, "gut gelaunt"),
    (1.0, "bester Laune"),
])
def test_stufen_der_laune(valenz, laune):
    assert f"Du bist {laune} und" in zustandsbericht(charakter_laden(), Zustand(valenz, 0.3))


@pytest.mark.parametrize(("erregung", "wort"), [
    (0.0, "ganz ruhig"),
    (0.3, "ruhig"),
    (0.6, "lebhaft"),
    (1.0, "aufgedreht"),
])
def test_stufen_der_erregung(erregung, wort):
    assert f"und {wort}." in zustandsbericht(charakter_laden(), Zustand(0.0, erregung))


def test_art_mit_niedrigen_und_hohen_werten():
    charakter = charakter_pruefen({
        "grundstimmung": 0.5, "reaktivitaet": 0.5, "rueckkehrstaerke": 0.5,
        "geselligkeit": 0.2, "neugier": 0.5, "vorsicht": 0.9, "ausdauer": 0.1,
    })
    assert "- Deine Art: zurückhaltend, vorsichtig und sprunghaft." in zustandsbericht(charakter, Zustand(0, 0.3))


def test_mittlerer_charakter_laesst_die_art_weg():
    mitte = dict.fromkeys(
        ["grundstimmung", "reaktivitaet", "rueckkehrstaerke", "geselligkeit", "neugier", "vorsicht", "ausdauer"], 0.5)
    assert "Deine Art" not in zustandsbericht(charakter_pruefen(mitte), Zustand(0, 0.3))


@pytest.mark.parametrize("valenz", [-1.0, -0.5, 0.0, 0.5, 1.0])
@pytest.mark.parametrize("erregung", [0.0, 0.4, 0.7, 1.0])
def test_keine_zahlen_im_text(valenz, erregung):
    assert not any(zeichen.isdigit() for zeichen in zustandsbericht(charakter_laden(), Zustand(valenz, erregung)))


def test_bericht_schreibt_nichts():
    charakter = charakter_laden()
    log = ErklaerLog(FesteUhr())
    zustand = grundzustand(charakter, log)
    vorher = list(log.eintraege)
    zustandsbericht(charakter, zustand)
    assert log.eintraege == vorher
    assert zustand == grundzustand(charakter, ErklaerLog(FesteUhr()))
