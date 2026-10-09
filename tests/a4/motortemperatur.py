"""Liest die Motortemperatur (Register 146) ueber den Raw-Endpunkt des Daemons. Sendet nur Lese-Pakete.

Aufruf (mit einer Umgebung, die `websockets` hat): python tests/a4/motortemperatur.py <Motor-Nr> [<Motor-Nr> ...]
"""

import asyncio
import sys

ADRESSE = "ws://192.168.178.101:8000/api/move/ws/raw/write"
LESEN = 0x02
REGISTER_TEMPERATUR = 146
KOPF = bytes([0xFF, 0xFF, 0xFD, 0x00])


def pruefsumme(daten: bytes) -> int:
    """CRC-16 des Dynamixel-Protokolls 2.0 (Polynom 0x8005, Startwert 0)."""
    crc = 0
    for byte in daten:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x8005 if crc & 0x8000 else crc << 1) & 0xFFFF
    return crc


def lesepaket(motor: int, register: int = REGISTER_TEMPERATUR, laenge: int = 1) -> bytes:
    """Baut ein Lese-Paket. Eine andere Anweisung als Lesen kann diese Funktion nicht erzeugen."""
    rumpf = KOPF + bytes([motor, 7, 0, LESEN, register & 0xFF, register >> 8, laenge & 0xFF, laenge >> 8])
    crc = pruefsumme(rumpf)
    return rumpf + bytes([crc & 0xFF, crc >> 8])


def nur_lesen(paket: bytes) -> bytes:
    """Letzte Sperre vor dem Senden: laesst ausschliesslich gueltige Lese-Pakete durch."""
    if len(paket) != 14 or paket[:4] != KOPF or paket[7] != LESEN or paket != lesepaket(paket[4], paket[8], paket[10]):
        raise ValueError("Kein reines Lese-Paket, wird nicht gesendet.")
    return paket


def temperatur(antwort: bytes, motor: int) -> int:
    """Liest den Wert aus dem Antwortpaket: Kopf, Motor, Laenge, 0x55, Fehler, Wert, CRC."""
    start = antwort.find(KOPF + bytes([motor]))
    if start < 0 or len(antwort) < start + 12 or antwort[start + 7] != 0x55:
        raise ValueError(f"Keine gültige Antwort: {antwort.hex(' ')}")
    paket = antwort[start : start + 12]
    if pruefsumme(paket[:-2]) != paket[-2] | paket[-1] << 8:
        raise ValueError(f"Prüfsumme falsch: {paket.hex(' ')}")
    if paket[8] != 0:
        raise ValueError(f"Motor meldet Fehler {paket[8]:#04x}")
    return paket[9]


async def main(motoren: list[int]) -> None:
    import websockets  # erst hier, damit die Tests ohne das Paket laufen

    async with websockets.connect(ADRESSE) as ws:
        for motor in motoren:
            await ws.send(nur_lesen(lesepaket(motor)))
            antwort = await asyncio.wait_for(ws.recv(), 3)
            try:
                print(f"Motor {motor}: {temperatur(antwort, motor)} °C")
            except ValueError as fehler:
                print(f"Motor {motor}: {fehler}")


if __name__ == "__main__":
    asyncio.run(main([int(nr) for nr in sys.argv[1:]]))
