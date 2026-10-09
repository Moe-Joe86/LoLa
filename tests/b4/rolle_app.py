"""Spielt die Rolle der Conversation App an der Realtime-Schnittstelle von speech-to-speech (nur für B4).

Sitzung mit unserem Profil und den Tools der App, dann Sätze als Text oder als Ton. Wird nie gemergt.
Läuft mit der Umgebung von speech-to-speech (braucht `websockets`).
"""

import ast
import asyncio
import base64
import json
import time
import wave
from pathlib import Path

import websockets

ADRESSE = "ws://127.0.0.1:8765/v1/realtime"
REPO = Path(__file__).resolve().parents[2]
APP = Path.home() / "lola-laufzeit" / "reachy_mini_conversation_app" / "src" / "reachy_mini_conversation_app"
AUFNAHMEN = Path.home() / "lola-laufzeit" / "messung" / "aufnahmen-synth"
STUECK = 320  # 20 ms bei 16 kHz


def profil() -> tuple[str, list[str]]:
    """Anweisungstext und Tool-Namen aus unserem Profil."""
    _, kopf, text = (REPO / "charakter/profile/lola_deutsch/profile.md").read_text(encoding="utf-8").split("+++", 2)
    namen = [zeile.strip(' ",') for zeile in kopf.splitlines() if zeile.strip().startswith('"')]
    return text.strip(), namen


def lade_tools(namen: list[str]) -> list[dict]:
    """Liest Name, Beschreibung und Schema der Tools aus dem Quelltext der App, ohne ihn auszuführen (wie A3)."""
    emotionen, tools = [], []
    for name in namen:
        felder = {}
        for knoten in ast.walk(ast.parse((APP / "tools" / f"{name}.py").read_text(encoding="utf-8"))):
            if isinstance(knoten, ast.AnnAssign) and getattr(knoten.target, "id", "") == "EMOTION_INTENTS":
                emotionen = list(ast.literal_eval(knoten.value))
            if isinstance(knoten, ast.Assign) and isinstance(knoten.targets[0], ast.Name):
                ziel = knoten.targets[0].id
                if ziel in ("name", "description", "parameters_schema"):
                    try:
                        felder[ziel] = ast.literal_eval(knoten.value)
                    except ValueError:
                        felder.setdefault(ziel, None)
        schema = felder.get("parameters_schema") or {"type": "object", "required": [], "properties": {}}
        if name == "dance":  # die Liste der Tänze entsteht erst zur Laufzeit der App, hier vereinfacht
            schema = {"type": "object", "required": [], "properties": {"move": {"type": "string"}}}
        if name == "play_emotion":
            schema = {
                "type": "object",
                "required": [],
                "properties": {"emotion": {"type": "string", "enum": emotionen}},
            }
        tools.append(
            {"type": "function", "name": felder["name"], "description": felder["description"], "parameters": schema}
        )
    return tools


class Sitzung:
    """Eine Realtime-Sitzung. `ereignisse` sammelt alles, was zurückkommt, mit Ankunftszeit."""

    async def __aenter__(self) -> "Sitzung":
        self.ereignisse: list[tuple[float, dict]] = []
        for _ in range(100):  # der Platz der vorigen Sitzung wird erst kurz nach deren Ende frei
            self.ws = await websockets.connect(ADRESSE, max_size=None)
            try:
                await self._bis("session.created")
                break
            except RuntimeError:
                await self.ws.close()
                await asyncio.sleep(0.2)
        text, namen = profil()
        pcm = {"type": "audio/pcm", "rate": None}
        eingang = {
            "format": pcm,
            "transcription": {"model": "gpt-4o-transcribe", "language": "auto"},
            "turn_detection": {"type": "server_vad", "interrupt_response": True},
        }
        sitzung = {
            "type": "realtime",
            "instructions": text,
            "tools": lade_tools(namen),
            "tool_choice": "auto",
            "audio": {"input": eingang, "output": {"format": pcm, "voice": "Aiden"}},
        }
        await self.ws.send(json.dumps({"type": "session.update", "session": sitzung}))
        await self._bis("session.updated")
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.ws.close()

    async def _bis(self, *arten: str, dauer: float = 60.0) -> dict:
        """Liest, bis ein Ereignis einer der Arten kommt. Ein Fehler-Ereignis bricht ab."""
        ende = time.monotonic() + dauer
        while True:
            ereignis = json.loads(await asyncio.wait_for(self.ws.recv(), max(ende - time.monotonic(), 0.01)))
            self.ereignisse.append((time.monotonic(), ereignis))
            if ereignis["type"] == "error":
                raise RuntimeError(ereignis)
            if ereignis["type"] in arten:
                return ereignis

    async def _antwort(self, beginn: float) -> dict:
        """Sammelt eine Antwort bis `response.done`: Text, Tool-Aufrufe, Zeit bis zum ersten Ton."""
        start = len(self.ereignisse)
        await self._bis("response.done", dauer=90.0)
        neu = self.ereignisse[start:]
        text = "".join(e.get("delta", "") for _, e in neu if e["type"].endswith("transcript.delta"))
        tools = [
            e["item"]
            for _, e in neu
            if e["type"] == "response.output_item.done" and e["item"]["type"] == "function_call"
        ]
        ton = [zeit for zeit, e in neu if e["type"] == "response.output_audio.delta"]
        return {
            "text": " ".join(text.split()),
            "tools": [(t["name"], t["arguments"]) for t in tools],
            "aufrufe": tools,
            "erster_ton_s": round(ton[0] - beginn, 3) if ton else None,
        }

    async def sage_text(self, satz: str) -> dict:
        """Schickt einen Satz als Text (so sendet auch `conversation.say`) und beantwortet Tool-Aufrufe wie die App."""
        nachricht = {"type": "message", "role": "user", "content": [{"type": "input_text", "text": satz}]}
        await self.ws.send(json.dumps({"type": "conversation.item.create", "item": nachricht}))
        beginn = time.monotonic()
        await self.ws.send(json.dumps({"type": "response.create"}))
        antwort = await self._antwort(beginn)
        for aufruf in antwort["aufrufe"]:
            ergebnis = {"type": "function_call_output", "call_id": aufruf["call_id"], "output": '{"status": "ok"}'}
            await self.ws.send(json.dumps({"type": "conversation.item.create", "item": ergebnis}))
        if antwort["aufrufe"]:
            await self.ws.send(json.dumps({"type": "response.create"}))
            antwort["danach"] = (await self._antwort(time.monotonic()))["text"]
        return antwort

    async def sage_ton(self, nummer: int, danach: int | None = None, pause: float = 0.0) -> dict:
        """Spielt eine Aufnahme im Takt der echten Zeit ein, dann Stille, und sammelt die Antwort.

        Mit `danach` folgt nach `pause` Sekunden Stille eine zweite Aufnahme: eine Sprechpause mitten im Satz.
        """
        daten = b""
        for teil in (nummer, danach):
            if teil is None:
                continue
            with wave.open(str(AUFNAHMEN / f"satz_{teil:02}.wav")) as datei:
                assert (datei.getframerate(), datei.getnchannels(), datei.getsampwidth()) == (16000, 1, 2)
                daten += bytes(int(pause * 16000) * 2 if daten else 0) + datei.readframes(datei.getnframes())
        stille = bytes(2 * STUECK)
        start = len(self.ereignisse)
        leser = asyncio.create_task(self._antwort(0.0))  # liest mit, während der Ton läuft
        takt = time.monotonic()
        satzende = None
        for stelle in range(0, len(daten) + 150 * 2 * STUECK, 2 * STUECK):  # Aufnahme, danach 3 s Stille
            stueck = daten[stelle : stelle + 2 * STUECK] or stille
            if stelle >= len(daten) and satzende is None:
                satzende = time.monotonic()
            ton = base64.b64encode(stueck.ljust(2 * STUECK, b"\0")).decode()
            await self.ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": ton}))
            takt += 0.02
            await asyncio.sleep(max(takt - time.monotonic(), 0))
            if leser.done():
                break
        try:
            antwort = await asyncio.wait_for(leser, 20)
        except (TimeoutError, asyncio.TimeoutError):  # keine Antwort, z. B. weil das Stück zu kurz war
            antwort = {"text": "", "tools": [], "aufrufe": [], "erster_ton_s": None}
        neu = self.ereignisse[start:]
        ton = [zeit for zeit, e in neu if e["type"] == "response.output_audio.delta"]
        erkannt = [e.get("transcript", "") for _, e in neu if e["type"].endswith("input_audio_transcription.completed")]
        antwort |= {
            "erkannt": erkannt[-1] if erkannt else "",
            "erster_ton_s": round(ton[0] - satzende, 3) if ton and satzende else None,
        }
        return antwort
