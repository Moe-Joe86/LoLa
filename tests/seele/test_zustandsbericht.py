import pytest

from seele.charakter import charakter_laden, charakter_pruefen
from seele.erklaer_log import ErklaerLog
from seele.zustand import Zustand, grundzustand
from seele.zustandsbericht import ERREGUNG, LAUNE, zustandsbericht
from tests.attrappen.uhr import FesteUhr


def test_bericht_fuer_reachy_im_grundzustand():
    charakter = charakter_laden()
    bericht = zustandsbericht(charakter, grundzustand(charakter, ErklaerLog(FesteUhr())))
    assert bericht == (
        "[Zustand] Du, LoLa, bist gut gelaunt und ruhig. Deine Art: gesellig und neugierig. "
        "Sprich freundlich und dabei ruhig und knapp, ohne Ausrufezeichen."
    )


def test_bericht_ist_ein_einzelner_eintrag_mit_kennung():
    bericht = zustandsbericht(charakter_laden(), Zustand(0.0, 0.3))
    assert bericht.startswith("[Zustand] Du, LoLa, bist ")
    assert "\n" not in bericht


def test_name_laesst_sich_setzen():
    bericht = zustandsbericht(charakter_laden(), Zustand(0.0, 0.3), name="Reachy")
    assert bericht.startswith("[Zustand] Du, Reachy, bist ")


@pytest.mark.parametrize(("valenz", "laune", "ton"), [
    (-1.0, "bedrückt", "ernst"),
    (-0.4, "etwas gedrückter Stimmung", "zurückhaltend"),
    (0.0, "ausgeglichen", "sachlich"),
    (0.3, "gut gelaunt", "freundlich"),
    (1.0, "bester Laune", "herzlich"),
])
def test_stufen_der_laune_mit_sprechanweisung(valenz, laune, ton):
    bericht = zustandsbericht(charakter_laden(), Zustand(valenz, 0.3))
    assert f"Du, LoLa, bist {laune} und" in bericht
    assert f"Sprich {ton} und dabei " in bericht


@pytest.mark.parametrize(("erregung", "wort", "tempo"), [
    (0.0, "ganz ruhig", "langsam und knapp, ohne Ausrufezeichen"),
    (0.3, "ruhig", "ruhig und knapp, ohne Ausrufezeichen"),
    (0.6, "lebhaft", "lebhaft"),
    (1.0, "aufgedreht", "schnell"),
])
def test_stufen_der_erregung_mit_sprechanweisung(erregung, wort, tempo):
    bericht = zustandsbericht(charakter_laden(), Zustand(0.0, erregung))
    assert f"und {wort}." in bericht
    assert bericht.endswith(f" und dabei {tempo}.")


@pytest.mark.parametrize("laune", LAUNE)
@pytest.mark.parametrize("erregung", ERREGUNG)
def test_bericht_besteht_nur_aus_festen_bausteinen(laune, erregung):
    """Jede Kombination ergibt genau den Rahmen mit Bausteinen aus der Tabelle, ohne Beispielsatz."""
    werte = Zustand(min(laune[0], 1.0) - 0.1, min(erregung[0], 1.0) - 0.1)
    bericht = zustandsbericht(charakter_laden(), werte)
    assert bericht == (
        f"[Zustand] Du, LoLa, bist {laune[1]} und {erregung[1]}. Deine Art: gesellig und neugierig. "
        f"Sprich {laune[2]} und dabei {erregung[2]}."
    )
    assert not any(zeichen in bericht for zeichen in "„“\"!?")


def test_art_mit_niedrigen_und_hohen_werten():
    charakter = charakter_pruefen({
        "grundstimmung": 0.5, "reaktivitaet": 0.5, "rueckkehrstaerke": 0.5,
        "geselligkeit": 0.2, "neugier": 0.5, "vorsicht": 0.9, "ausdauer": 0.1,
    })
    bericht = zustandsbericht(charakter, Zustand(0, 0.3))
    assert " Deine Art: zurückhaltend, vorsichtig und sprunghaft. Sprich " in bericht


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
