"""Liest je Motor Temperatur (Register 146) und Hardware-Fehlerstatus (Register 70). Sendet nur Lese-Pakete.

Aufruf (Umgebung mit `websockets`): python tests/a4/motorstatus.py <Motor-Nr> [<Motor-Nr> ...]
"""

import asyncio
import sys
import time

from motortemperatur import ADRESSE, REGISTER_TEMPERATUR, lesepaket, nur_lesen, temperatur

REGISTER_FEHLERSTATUS = 70
BITS = {0: "Eingangsspannung", 2: "Überhitzung", 3: "Encoder", 4: "elektrischer Schlag", 5: "Überlast"}


async def lies(ws, motor: int, register: int) -> tuple[int, bool, bytes, float]:
    paket = nur_lesen(lesepaket(motor, register))
    beginn = time.monotonic()
    await ws.send(paket)
    antwort = await asyncio.wait_for(ws.recv(), 3)
    wert, warnung = temperatur(antwort, motor)  # gleiche Paketform: ein Byte Nutzlast
    return wert, warnung, antwort, time.monotonic() - beginn


async def main(motoren: list[int]) -> None:
    import websockets

    async with websockets.connect(ADRESSE) as ws:
        for motor in motoren:
            try:
                grad, warnung, _, dauer = await lies(ws, motor, REGISTER_TEMPERATUR)
                status, _, roh, _ = await lies(ws, motor, REGISTER_FEHLERSTATUS)
                gruende = [name for bit, name in BITS.items() if status >> bit & 1] or ["keiner"]
                print(
                    f"Motor {motor}: {grad} °C, Warn-Bit {'ja' if warnung else 'nein'}, Fehlerstatus "
                    f"0x{status:02x} ({', '.join(gruende)}), Antwort nach {dauer * 1000:.0f} ms | {roh.hex(' ')}"
                )
            except (ValueError, TimeoutError) as fehler:
                print(f"Motor {motor}: {fehler}")


if __name__ == "__main__":
    asyncio.run(main([int(nr) for nr in sys.argv[1:]]))
