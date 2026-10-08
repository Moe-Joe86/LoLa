"""A1 Schritt 5: die sechs Nachprüfungen aus A2, Proxy aus test/vermittler gegen das echte llama.cpp.

Braucht: llama-server auf Port 8090, die Umgebung von speech-to-speech (Commit 8024ccf) und den
ausgecheckten Branch test/vermittler im PYTHONPATH (dessen Wurzel und dessen tests/).
Aufruf: PYTHONPATH=<test/vermittler>:<test/vermittler>/tests python a2_nachpruefung.py
Gibt ein Protokoll in Markdown aus.
"""

import copy
import json
import threading
import time
import urllib.error
import urllib.request

from a2_lauf import BERICHT, BEWEGUNG, baue_anfrage, lauf, neuer_handler  # aus test/vermittler, mit echtem Handler
from attrappen.llama_attrappe import starte_attrappe
from speech_to_speech.LLM.chat import make_user_message
from speech_to_speech.LLM.responses_api_language_model import ResponsesApiModelHandler
from speech_to_speech.pipeline.messages import EndOfResponse, LLMResponseChunk
from vermittler.proxy import Einstellung, starte_server

LLAMA, PROXY, ATTRAPPE = 8090, 8091, 8092
ZIEL = f"http://127.0.0.1:{LLAMA}"
BERICHT_2 = "[Zustand] Reachy ist wach, gut gelaunt und neugierig."
NUTZERSAETZE = ["Kannst du für mich tanzen?", "Wie geht es dir?", "Ja.", "Wie spät ist es?", "Erzähl mir einen Witz."]


def echte_anfrage() -> dict:
    """Lässt den echten Handler einmal gegen die Attrappe laufen und gibt seine Streaming-Anfrage zurück."""
    server, aufzeichnung = starte_attrappe(ATTRAPPE)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    handler = object.__new__(ResponsesApiModelHandler)
    ResponsesApiModelHandler.setup(
        handler, model_name="qwen3", base_url=f"http://127.0.0.1:{ATTRAPPE}/v1",
        stream=True, disable_thinking=True, reasoning_effort="none", stream_batch_sentences=1)
    list(handler.process(baue_anfrage()))
    server.shutdown()
    server.server_close()
    return json.loads(aufzeichnung.anfragen[-1]["koerper"])


def handler_text(port: int) -> dict:
    """Echter Handler mit einer Frage, die Text statt eines Tool-Aufrufs verlangt."""
    anfrage = baue_anfrage()
    anfrage.runtime_config.chat.add_item(make_user_message("Nein, lieber doch nicht. Wie geht es dir heute?"))
    start, stuecke, fehler = time.perf_counter(), [], None
    for ausgabe in neuer_handler(port).process(anfrage):
        if isinstance(ausgabe, EndOfResponse):
            fehler = ausgabe.error
        elif isinstance(ausgabe, LLMResponseChunk) and ausgabe.text:
            stuecke.append((round(time.perf_counter() - start, 2), ausgabe.text))
    return {"stuecke": stuecke, "fehler": fehler}


def sende(port: int, anfrage: dict, abbruch_nach_text: bool = False) -> dict:
    """Schickt eine Streaming-Anfrage roh und sammelt, was zurückkommt."""
    daten = json.dumps(anfrage, ensure_ascii=False).encode("utf-8")
    http_anfrage = urllib.request.Request(
        f"http://127.0.0.1:{port}/v1/responses", daten, {"Content-Type": "application/json"})
    e = {"status": None, "fehler": None, "typen": {}, "text": "", "tools": [], "nutzung": None, "erstes_s": None}
    start = time.perf_counter()
    try:
        antwort = urllib.request.urlopen(http_anfrage, timeout=120)
    except urllib.error.HTTPError as fehler:
        e["status"], e["fehler"] = fehler.code, fehler.read().decode("utf-8", "replace")[:400]
        return e
    e["status"] = antwort.status
    for zeile in antwort:
        zeile = zeile.decode("utf-8").strip()
        if not zeile.startswith("data: ") or zeile == "data: [DONE]":
            continue
        ereignis = json.loads(zeile[6:])
        typ = ereignis.get("type", "?")
        e["typen"][typ] = e["typen"].get(typ, 0) + 1
        if typ == "response.output_text.delta":
            e["erstes_s"] = e["erstes_s"] or round(time.perf_counter() - start, 3)
            e["text"] += ereignis["delta"]
            if abbruch_nach_text:
                break
        elif typ == "response.output_item.done" and ereignis["item"].get("type") == "function_call":
            e["tools"].append(f"{ereignis['item']['name']}({ereignis['item']['arguments']})")
        elif typ == "response.completed":
            e["nutzung"] = ereignis["response"].get("usage")
        elif typ in ("error", "response.failed"):
            e["fehler"] = json.dumps(ereignis, ensure_ascii=False)[:400]
    antwort.close()
    e["gesamt_s"] = round(time.perf_counter() - start, 3)
    return e


class Proxy:
    """Startet den Vermittler aus test/vermittler für die Dauer eines with-Blocks."""

    def __init__(self, **einstellung) -> None:
        self.server = starte_server(PROXY, Einstellung(ziel=ZIEL, **einstellung))

    def __enter__(self) -> int:
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return PROXY

    def __exit__(self, *_) -> None:
        self.server.shutdown()
        self.server.server_close()


def kurz(e: dict) -> str:
    text = " ".join(e["text"].split())[:220]
    return f"HTTP {e['status']}, Fehler {e['fehler']}, Tools {e['tools']}, Text: „{text}“"


def mit_satz(anfrage: dict, satz: str) -> dict:
    neu = copy.deepcopy(anfrage)
    neu["input"][-1]["content"][0]["text"] = satz
    return neu


def naechste_runde(anfrage: dict, antwort: str, satz: str) -> dict:
    """Hängt die Antwort des Modells und einen neuen Nutzersatz an, wie es speech-to-speech täte."""
    neu = copy.deepcopy(anfrage)
    neu["input"].append({"type": "message", "role": "assistant",
                         "content": [{"type": "output_text", "text": antwort or "Na klar."}]})
    neu["input"].append({"type": "message", "role": "user", "content": [{"type": "input_text", "text": satz}]})
    return neu


def arbeitet() -> bool:
    with urllib.request.urlopen(f"{ZIEL}/slots", timeout=5) as antwort:
        return any(slot.get("is_processing") for slot in json.loads(antwort.read()))


LANG = {"model": "qwen3", "stream": True, "reasoning": {"effort": "none"}, "max_output_tokens": 3000,
            "input": [{"type": "message", "role": "user", "content": [{"type": "input_text", "text":
                       "Erzähl mir eine sehr lange Geschichte über einen Drachen, mindestens zweitausend Wörter."}]}]}


def gegenprobe() -> str:
    """Ohne Abbruch: Meldet /slots während der Erzeugung wirklich Arbeit?"""
    ergebnis = {}
    faden = threading.Thread(target=lambda: ergebnis.update(sende(LLAMA, LANG)))
    faden.start()
    time.sleep(1.0)
    mittendrin = arbeitet()
    faden.join()
    return (f"nach 1 s arbeitet llama.cpp: {mittendrin}; ohne Abbruch lief die Erzeugung {ergebnis['gesamt_s']} s "
            f"({ergebnis['nutzung']['output_tokens']} Token)")


def pruefe_abbruch(port: int) -> str:
    sende(port, LANG, abbruch_nach_text=True)
    start = time.perf_counter()
    while arbeitet() and time.perf_counter() - start < 30:
        time.sleep(0.05)
    dauer = time.perf_counter() - start
    zusatz = " (ABBRUCH NICHT ERKANNT)" if dauer >= 30 else ""
    return f"llama.cpp rechnete nach dem Schließen noch {dauer:.2f} s weiter{zusatz}"


def pruefe_zwischenspeicher(basis: dict, art: str | None) -> str:
    def runde(anfrage: dict, bericht: str) -> dict:
        if art is None:
            return sende(LLAMA, anfrage)
        with Proxy(bericht=bericht, bericht_art=art) as port:
            return sende(port, anfrage)

    sende(LLAMA, {"model": "qwen3", "stream": True, "reasoning": {"effort": "none"}, "max_output_tokens": 8,
                  "input": "Sag nur das Wort Test."})
    eins = runde(basis, BERICHT)
    zwei = runde(naechste_runde(basis, eins["text"], "Und wie geht es dir heute?"), BERICHT_2)
    if zwei["nutzung"] is None:
        return f"Runde 2 fehlgeschlagen: {kurz(zwei)}"
    n1, n2 = eins["nutzung"], zwei["nutzung"]
    return (f"Runde 1: {n1['input_tokens']} Eingabe-Token, erster Text nach {eins['erstes_s']} s. "
            f"Runde 2: {n2['input_tokens']} Eingabe-Token, davon {n2['input_tokens_details']['cached_tokens']} "
            f"aus dem Zwischenspeicher, erster Text nach {zwei['erstes_s']} s")


def main() -> None:
    basis = echte_anfrage()
    print("## Lauf", time.strftime("%Y-%m-%d %H:%M:%S"), "\n")

    print("### 1 `/v1/responses` mit Tools und Streaming")
    direkt = sende(LLAMA, basis)
    print("- roh, ohne Proxy:", kurz(direkt))
    print("- Ereignistypen:", json.dumps(direkt["typen"]))
    print("- echter Handler ohne Proxy:", lauf(LLAMA))
    with Proxy() as port:
        print("- echter Handler über den Proxy:", lauf(port))
        print("- echter Handler über den Proxy, Textantwort:", handler_text(port))

    print("\n### 2 Bericht als letzter Eintrag (System hinter dem Nutzersatz)")
    with Proxy(bericht=BERICHT, bericht_art="eintrag") as port:
        eintrag = sende(port, basis)
        print("-", kurz(eintrag))
        for satz in NUTZERSAETZE[1:]:
            print(f"- „{satz}“ →", kurz(sende(port, mit_satz(basis, satz))))

    print("\n### 3 Bericht an der letzten Nutzer-Nachricht")
    with Proxy(bericht=BERICHT, bericht_art="nutzer") as port:
        for satz in NUTZERSAETZE:
            print(f"- „{satz}“ →", kurz(sende(port, mit_satz(basis, satz))))

    print("\n### 4 Zwischenspeicher über zwei Runden")
    print("- ohne Bericht:", pruefe_zwischenspeicher(basis, None))
    if eintrag["status"] == 200 and eintrag["fehler"] is None:
        print("- Bericht als Eintrag:", pruefe_zwischenspeicher(basis, "eintrag"))
    print("- Bericht an Nutzer-Nachricht:", pruefe_zwischenspeicher(basis, "nutzer"))

    print("\n### 5 Tool fehlt, das im Verlauf aufgerufen wurde", sorted(BEWEGUNG))
    with Proxy(ohne_tools=BEWEGUNG) as port:
        print("-", kurz(sende(port, basis)))
        print("- echter Handler:", lauf(port))

    print("\n### 6 Abbruch, wenn die Verbindung schließt")
    print("- Gegenprobe:", gegenprobe())
    print("- ohne Proxy:", pruefe_abbruch(LLAMA))
    with Proxy() as port:
        print("- über den Proxy:", pruefe_abbruch(port))
        print("- nächste Anfrage über denselben Proxy:", kurz(sende(port, basis)))

    print("\n### Gesendete Anfrage (echter Handler)\n```json")
    print(json.dumps(basis, ensure_ascii=False, indent=1)[:6000])
    print("```")


if __name__ == "__main__":
    main()
