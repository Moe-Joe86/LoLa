"""A1 Schritt 4: Gesamtkette mit gespeicherten Aufnahmen statt Mikrofon.

Erkennung (Parakeet, CPU), Sprachmodell (echter Handler von speech-to-speech gegen llama-server auf
Port 8090) und Sprachausgabe (Qwen3-TTS, GGML) laufen gleichzeitig in einem Prozess, wie in der
Sprachkette. Die Uhr startet, wenn die Aufnahme vollständig vorliegt (Satzende). Die Wartezeit der
Pausenerkennung davor ist nicht enthalten. Das Sprachmodell erzeugt weiter, während der erste Ton entsteht.
Aufruf (Umgebung wie a2_nachpruefung.py, dazu OMP_NUM_THREADS=6):
    python kette_messen.py --aufnahmen ORDNER [--laeufe 3] [--buendel 1]
"""

import argparse
import json
import os
import queue
import statistics
import subprocess
import threading
import time
from pathlib import Path

import soundfile as sf
from a2_lauf import TOOLS  # aus test/vermittler: die vier nachgebildeten Tools
from openai.types.realtime import RealtimeSessionCreateRequest
from speech_to_speech.api.openai_realtime.runtime_config import RuntimeConfig
from speech_to_speech.LLM.chat import Chat, make_user_message
from speech_to_speech.LLM.responses_api_language_model import ResponsesApiModelHandler
from speech_to_speech.pipeline.messages import GenerateResponseRequest, LLMResponseChunk

LLAMA = 8090
ANWEISUNG = "Du bist Reachy, ein freundlicher Roboter. Sprich Deutsch. Antworte kurz, in ein bis zwei Sätzen."
ERSTE = ("response.output_text.delta", "response.function_call_arguments.delta")


def gesamt_mib() -> int:
    aus = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=False).stdout
    return int(aus.strip().splitlines()[0])


def prozesse_mib() -> dict[str, int]:
    """Grafikspeicher dieses Prozesses und des llama-servers laut nvidia-smi."""
    aus = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,name,used_memory", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=False).stdout
    werte = {"kette": 0, "llama": 0}
    for zeile in aus.splitlines():
        pid, name, mib = (teil.strip() for teil in zeile.split(","))
        if int(pid) == os.getpid():
            werte["kette"] = int(mib)
        elif "llama-server" in name:
            werte["llama"] = int(mib)
    return werte


def lade_sprachmodell(buendel: int, uhr: dict) -> ResponsesApiModelHandler:
    """Echter Handler; der Strom wird umhüllt, um das erste Token zu stoppen."""
    handler = object.__new__(ResponsesApiModelHandler)
    ResponsesApiModelHandler.setup(
        handler, model_name="qwen3", base_url=f"http://127.0.0.1:{LLAMA}/v1",
        stream=True, disable_thinking=True, reasoning_effort="none", stream_batch_sentences=buendel)
    anfrage_echt = handler._request

    def anfrage(api_input, optional_kwargs):
        for ereignis in anfrage_echt(api_input, optional_kwargs):
            if uhr.get("token") is None and getattr(ereignis, "type", "") in ERSTE:
                uhr["token"] = time.perf_counter()
            yield ereignis

    handler._request = anfrage
    return handler


def eine_runde(ton, erkenne, handler, tts, sprecher: str, uhr: dict) -> dict:
    uhr["token"] = None
    start = time.perf_counter()
    text = erkenne(ton).strip()
    erkannt = time.perf_counter()
    chat = Chat(20)
    chat.add_item(make_user_message(text or "..."))
    sitzung = RealtimeSessionCreateRequest(type="realtime", instructions=ANWEISUNG, tools=TOOLS, tool_choice="auto")
    anfrage = GenerateResponseRequest(runtime_config=RuntimeConfig(chat=chat, session=sitzung))
    stuecke: queue.Queue = queue.Queue()

    def erzeuge() -> None:
        for ausgabe in handler.process(anfrage):
            if isinstance(ausgabe, LLMResponseChunk) and (ausgabe.text or ausgabe.tools):
                stuecke.put((time.perf_counter(), ausgabe.text, [t.name for t in ausgabe.tools]))
        stuecke.put(None)

    faden = threading.Thread(target=erzeuge)
    faden.start()
    satz_da, antwort, tools, ton_da = None, "", [], None
    while (stueck := stuecke.get()) is not None:
        tools += stueck[2]
        if stueck[1] and ton_da is None:
            satz_da, antwort = stueck[0], stueck[1]
            strom = tts.generate_custom_voice_streaming(text=antwort, speaker=sprecher, language="german", chunk_size=8)
            next(iter(strom))
            ton_da = time.perf_counter()
            strom.close()
    faden.join()
    ende = time.perf_counter()
    e = {"erkannt": text, "antwort": antwort, "tools": tools, "erkennung_s": erkannt - start,
         "erstes_token_s": (uhr["token"] - erkannt) if uhr["token"] else None, "alles_fertig_s": ende - start}
    if ton_da:
        e |= {"erster_satz_s": satz_da - uhr["token"], "erster_ton_s": ton_da - satz_da, "gesamt_s": ton_da - start}
    return e


def mittel(runden: list[dict], feld: str) -> dict | None:
    werte = [r[feld] for r in runden if r.get(feld) is not None]
    if not werte:
        return None
    return {"mittel": round(statistics.mean(werte), 3), "median": round(statistics.median(werte), 3),
            "max": round(max(werte), 3), "n": len(werte)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aufnahmen", type=Path, required=True)
    parser.add_argument("--laeufe", type=int, default=3)
    parser.add_argument("--buendel", type=int, default=1, help="Sätze, die das Sprachmodell sammelt (Standard dort: 3)")
    parser.add_argument("--tts_modell", default="0.6B-CustomVoice")
    parser.add_argument("--quant", default="Q8_0")
    parser.add_argument("--sprecher", default="aiden")
    parser.add_argument("--ziel", type=Path, required=True)
    args = parser.parse_args()

    vorher = {"gesamt_mib": gesamt_mib(), **prozesse_mib()}
    from faster_qwen3_tts import FasterQwen3TTS
    from nano_parakeet import from_pretrained

    parakeet = from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v3", device="cpu")
    tts = FasterQwen3TTS.from_pretrained(
        f"Qwen/Qwen3-TTS-12Hz-{args.tts_modell}", device="cuda", backend="ggml", quant=args.quant)
    uhr: dict = {}
    handler = lade_sprachmodell(args.buendel, uhr)
    toene = [sf.read(datei, dtype="float32")[0] for datei in sorted(args.aufnahmen.glob("satz_*.wav"))]
    eine_runde(toene[5], parakeet.transcribe, handler, tts, args.sprecher, uhr)

    runden, spitze = [], {"gesamt_mib": gesamt_mib(), **prozesse_mib()}
    for lauf in range(1, args.laeufe + 1):
        for nummer, ton in enumerate(toene, 1):
            runde = eine_runde(ton, parakeet.transcribe, handler, tts, args.sprecher, uhr)
            runden.append({"lauf": lauf, "satz": nummer, **runde})
            jetzt = {"gesamt_mib": gesamt_mib(), **prozesse_mib()}
            spitze = {k: max(spitze[k], jetzt[k]) for k in spitze}
            print(f"{lauf}/{nummer:02d} {runde.get('gesamt_s') or float('nan'):.3f} s  „{runde['erkannt']}“ → "
                  f"„{runde['antwort']}“ {runde['tools']}", flush=True)
    ergebnis = {
        "threads": os.environ.get("OMP_NUM_THREADS"), "buendel": args.buendel, "sprachausgabe":
        f"{args.tts_modell} {args.quant} {args.sprecher}", "vram_vorher": vorher, "vram_spitze": spitze,
        "runden_gesamt": len(runden), "runden_mit_ton": sum(1 for r in runden if r.get("gesamt_s")),
        "runden_nur_tool": sum(1 for r in runden if r["tools"] and not r["antwort"]),
        **{feld: mittel(runden, feld) for feld in
           ("erkennung_s", "erstes_token_s", "erster_satz_s", "erster_ton_s", "gesamt_s", "alles_fertig_s")},
    }
    args.ziel.write_text(json.dumps({"zusammenfassung": ergebnis, "runden": runden}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print("ERGEBNIS " + json.dumps(ergebnis, ensure_ascii=False))


if __name__ == "__main__":
    main()
