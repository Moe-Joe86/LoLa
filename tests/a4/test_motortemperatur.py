import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("mt", Path(__file__).with_name("motortemperatur.py"))
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)


def test_pruefsumme_stimmt_mit_dem_handbuch_ueberein():
    # Beispiel aus dem Handbuch von Robotis: Lesen, Motor 1, Register 132, 4 Bytes
    assert mt.lesepaket(1, 132, 4) == bytes.fromhex("FFFFFD000107000284000400" "1D15")


def test_jedes_paket_fuer_jeden_motor_ist_ein_lese_paket_auf_register_146():
    for motor in range(253):
        paket = mt.lesepaket(motor)
        assert paket[7] == 0x02
        assert (paket[8] | paket[9] << 8, paket[10] | paket[11] << 8) == (146, 1)
        assert mt.nur_lesen(paket) == paket


@pytest.mark.parametrize("anweisung", [0x01, 0x03, 0x04, 0x05, 0x06, 0x08, 0x10, 0x82, 0x83, 0x93])
def test_sperre_weist_jede_andere_anweisung_ab(anweisung):
    rumpf = bytearray(mt.lesepaket(15)[:-2])
    rumpf[7] = anweisung
    crc = mt.pruefsumme(bytes(rumpf))
    with pytest.raises(ValueError):
        mt.nur_lesen(bytes(rumpf) + bytes([crc & 0xFF, crc >> 8]))


def test_sperre_weist_verlaengerte_pakete_ab():
    with pytest.raises(ValueError):
        mt.nur_lesen(mt.lesepaket(15) + b"\x00")


def antwort(fehler: int, wert: int) -> bytes:
    rumpf = mt.KOPF + bytes([15, 5, 0, 0x55, fehler, wert])
    crc = mt.pruefsumme(rumpf)
    return rumpf + bytes([crc & 0xFF, crc >> 8])


def test_temperatur_aus_antwort():
    assert mt.temperatur(antwort(0, 37), 15) == (37, False)


def test_echte_antwort_von_motor_15_mit_warn_bit():
    assert mt.temperatur(bytes.fromhex("fffffd000f050055801b0c71"), 15) == (27, True)


def test_temperatur_meldet_abgelehnte_anfrage():
    with pytest.raises(ValueError):
        mt.temperatur(antwort(0x04, 0), 15)
