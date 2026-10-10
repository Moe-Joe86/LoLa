"""A7, hörbare Probe: nimmt über einen zweiten WebRTC-Strom das Mikrofon des Reachy auf, während die App läuft,
und spielt die Aufnahme danach über denselben Strom auf dem Lautsprecher des Reachy ab. Auf dem Reachy wird
nichts gespeichert; die Aufnahme liegt nur lokal. Während des Abspielens ist das Mikrofon der App stumm.

Aufruf mit der Umgebung der App: ~/lola-laufzeit/app-venv/bin/python tests/a7/hoerprobe.py <Sekunden> <Zielordner>
"""

import asyncio
import json
import sys
import time
import wave
from pathlib import Path

import numpy as np
import websockets
from reachy_mini.media.camera_constants import ReachyMiniWirelessCamSpecs
from reachy_mini.media.webrtc_client_gstreamer import GstWebRTCClient
from reachy_mini.media.webrtc_utils import find_producer_peer_id_by_name

REACHY = "reachy-mini.local"


async def mikro(stumm: bool) -> None:
    async with websockets.connect("ws://127.0.0.1:7860/rpc", max_size=None) as ws:
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "conversation.mic", "params": {"muted": stumm}}))
        while json.loads(await asyncio.wait_for(ws.recv(), 10)).get("id") != 1:
            pass


def main(dauer: float, ziel: Path) -> None:
    ziel.mkdir(parents=True, exist_ok=True)
    kunde = GstWebRTCClient(
        peer_id=find_producer_peer_id_by_name(REACHY, 8443, "reachymini"),
        signaling_host=REACHY,
        camera_specs=ReachyMiniWirelessCamSpecs(),
    )
    kunde.open()
    stuecke, zeiten, start = [], [], None
    while start is None or time.time() - start < dauer:
        stueck = kunde.get_audio_sample()
        if stueck is None or not len(stueck):
            continue
        start = start or time.time()
        stuecke.append(np.asarray(stueck, dtype=np.float32))
        zeiten.append(time.time())
    ton = np.concatenate(stuecke)
    luecken = [round(b - a, 3) for a, b in zip(zeiten, zeiten[1:], strict=False) if b - a > 0.1]
    print(f"aufgenommen: {len(ton) / kunde.SAMPLE_RATE:.1f} s Ton in {zeiten[-1] - zeiten[0]:.1f} s, Form {ton.shape}, "
          f"Lücken über 0,1 s: {luecken}", flush=True)  # fmt: skip
    with wave.open(str(ziel / "hoerprobe.wav"), "wb") as datei:
        datei.setparams((ton.shape[1] if ton.ndim > 1 else 1, 2, kunde.SAMPLE_RATE, 0, "NONE", "not compressed"))
        datei.writeframes((np.clip(ton, -1, 1) * 32767).astype(np.int16).tobytes())
    asyncio.run(mikro(True))
    print("spiele auf dem Reachy ab …", flush=True)
    schritt, takt = kunde.SAMPLE_RATE // 50, time.monotonic()
    for stelle in range(0, len(ton), schritt):
        kunde.push_audio_sample(ton[stelle : stelle + schritt])
        takt += 0.02
        time.sleep(max(takt - time.monotonic(), 0))
    time.sleep(1.5)
    asyncio.run(mikro(False))
    kunde.close()
    print("fertig", flush=True)


if __name__ == "__main__":
    main(float(sys.argv[1]), Path(sys.argv[2]).expanduser())
