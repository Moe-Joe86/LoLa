import pytest

from seele.charakter import Charakter, CharakterFehler, charakter_laden, charakter_pruefen

GUELTIG = {
    "grundstimmung": 0.65,
    "reaktivitaet": 0.5,
    "rueckkehrstaerke": 0.6,
    "geselligkeit": 0.7,
    "neugier": 0.7,
    "vorsicht": 0.5,
    "ausdauer": 0.6,
}


def test_reachy_toml_hat_die_vereinbarten_werte():
    assert charakter_laden() == Charakter(**GUELTIG)


def test_laden_aus_eigener_datei(tmp_path):
    datei = tmp_path / "test.toml"
    datei.write_text("\n".join(f"{name} = {wert}" for name, wert in GUELTIG.items()), encoding="utf-8")
    assert charakter_laden(datei).neugier == 0.7


def test_ganze_zahlen_an_den_grenzen_sind_erlaubt():
    charakter = charakter_pruefen(GUELTIG | {"vorsicht": 0, "ausdauer": 1})
    assert (charakter.vorsicht, charakter.ausdauer) == (0.0, 1.0)


def test_fehlender_wert_wird_genannt():
    werte = dict(GUELTIG)
    del werte["neugier"]
    with pytest.raises(CharakterFehler, match="fehlende Werte: neugier"):
        charakter_pruefen(werte)


def test_tippfehler_zeigt_fehlend_und_unbekannt():
    werte = dict(GUELTIG)
    werte["neugir"] = werte.pop("neugier")
    with pytest.raises(CharakterFehler, match="fehlende Werte: neugier.*unbekannte Werte: neugir"):
        charakter_pruefen(werte)


@pytest.mark.parametrize("wert", [-0.1, 1.5])
def test_wert_ausserhalb_0_bis_1(wert):
    with pytest.raises(CharakterFehler, match="vorsicht .* liegt nicht zwischen 0 und 1"):
        charakter_pruefen(GUELTIG | {"vorsicht": wert})


@pytest.mark.parametrize("wert", ["hoch", True])
def test_wert_ist_keine_zahl(wert):
    with pytest.raises(CharakterFehler, match="vorsicht ist keine Zahl"):
        charakter_pruefen(GUELTIG | {"vorsicht": wert})


def test_alle_probleme_auf_einmal():
    with pytest.raises(CharakterFehler) as fehler:
        charakter_pruefen(GUELTIG | {"neugier": 2, "ausdauer": -1})
    assert "neugier" in str(fehler.value) and "ausdauer" in str(fehler.value)
