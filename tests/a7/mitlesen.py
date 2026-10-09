"""Zweites Programm: liest Ton und Bild des Reachy per WebRTC mit, waehrend die App laeuft (nur lesen).

Aufruf mit der Umgebung der App: ~/lola-laufzeit/app-venv/bin/python tests/a7/mitlesen.py <Sekunden> <Zielordner>
Schreibt je Bild und je Tonstueck eine Zeile JSON, dazu ein Bild (PNG) und 15 s Ton (WAV). Alles bleibt lokal.
"""

import json
import struct
import sys
import threading
import time
import wave
import zlib
from pathlib import Path

import numpy as np
from reachy_mini.media.camera_constants import ReachyMiniWirelessCamSpecs
from reachy_mini.media.webrtc_client_gstreamer import GstWebRTCClient
from reachy_mini.media.webrtc_utils import find_producer_peer_id_by_name

REACHY = "reachy-mini.local"
TON_SEKUNDEN = int(sys.argv[3]) if len(sys.argv) > 3 else 15


def schreibe_png(datei: Path, bild: np.ndarray) -> None:
    """Speichert ein BGR-Bild als PNG, nur mit der Standardbibliothek."""
    hoehe, breite, _ = bild.shape
    zeilen = b"".join(b"\x00" + bild[y, :, ::-1].tobytes() for y in range(hoehe))

    def stueck(art: bytes, daten: bytes) -> bytes:
        return struct.pack(">I", len(daten)) + art + daten + struct.pack(">I", zlib.crc32(art + daten))

    kopf = struct.pack(">IIBBBBB", breite, hoehe, 8, 2, 0, 0, 0)
    inhalt = stueck(b"IHDR", kopf) + stueck(b"IDAT", zlib.compress(zeilen)) + stueck(b"IEND", b"")
    datei.write_bytes(b"\x89PNG\r\n\x1a\n" + inhalt)


def schaerfe(bild: np.ndarray) -> float:
    """Streuung des Laplace-Filters auf dem Graubild: je hoeher, desto schaerfer."""
    grau = bild.mean(axis=2)
    laplace = grau[1:-1, 1:-1] * 4 - grau[:-2, 1:-1] - grau[2:, 1:-1] - grau[1:-1, :-2] - grau[1:-1, 2:]
    return float(laplace.var())


def main(dauer: float, ziel: Path) -> None:
    ziel.mkdir(parents=True, exist_ok=True)
    kunde = GstWebRTCClient(
        peer_id=find_producer_peer_id_by_name(REACHY, 8443, "reachymini"),
        signaling_host=REACHY,
        camera_specs=ReachyMiniWirelessCamSpecs(),
    )
    kunde.open()
    ton, zeilen, letztes, bild_gespeichert = [], [], None, False
    start = time.time()

    def lies_ton() -> None:
        while time.time() - start < dauer:
            stueck = kunde.get_audio_sample()
            if stueck is None or not len(stueck):
                continue
            pegel = float(np.sqrt(np.mean(np.square(stueck))))
            zeilen.append({"t": time.time(), "art": "ton", "werte": len(stueck), "pegel": round(pegel, 5)})
            if sum(len(s) for s in ton) < TON_SEKUNDEN * kunde.SAMPLE_RATE:
                ton.append(stueck.copy())

    faden = threading.Thread(target=lies_ton)
    faden.start()
    while time.time() - start < dauer:
        bild = kunde.read()
        if bild is None:
            continue
        klein = bild[::8, ::8].astype(np.int16)
        aenderung = float(np.abs(klein - letztes).mean()) if letztes is not None else 0.0
        letztes = klein
        eintrag = {"t": time.time(), "art": "bild", "form": bild.shape, "aenderung": round(aenderung, 3)}
        if not bild_gespeichert and time.time() - start > 10:
            eintrag["schaerfe"] = round(schaerfe(bild), 1)
            schreibe_png(ziel / "bild.png", bild)
            bild_gespeichert = True
        zeilen.append(eintrag)
    faden.join()
    zeilen.sort(key=lambda zeile: zeile["t"])
    (ziel / "mitlesen.jsonl").write_text("\n".join(json.dumps(zeile) for zeile in zeilen), encoding="utf-8")
    kunde.close()
    if ton:
        daten = np.concatenate(ton)
        with wave.open(str(ziel / "ton.wav"), "wb") as datei:
            datei.setnchannels(daten.shape[1] if daten.ndim > 1 else 1)
            datei.setsampwidth(2)
            datei.setframerate(kunde.SAMPLE_RATE)
            datei.writeframes((np.clip(daten, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"fertig: Abtastrate {kunde.SAMPLE_RATE}, Kanäle {kunde.CHANNELS}")


if __name__ == "__main__":
    main(float(sys.argv[1]), Path(sys.argv[2]).expanduser())
