"""Machbarkeitstest A2: echter speech-to-speech-Handler -> Vermittler -> llama.cpp-Attrappe.

Läuft nicht mit pytest, sondern in einer Wegwerf-Umgebung mit speech-to-speech (Repo-Wurzel):
    PYTHONPATH=<klon>/src:.:tests NLTK_DATA=<pfad> python tests/vermittler/a2_lauf.py
Gibt ein Protokoll in Markdown aus.
"""

import itertools
import json
import threading
import time

from attrappen.llama_attrappe import starte_attrappe
from openai import OpenAI
from openai.types.realtime import RealtimeSessionCreateRequest
from openai.types.realtime.conversation_item import (
    RealtimeConversationItemAssistantMessage,
    RealtimeConversationItemFunctionCall,
    RealtimeConversationItemFunctionCallOutput,
)
from speech_to_speech.api.openai_realtime.runtime_config import RuntimeConfig
from speech_to_speech.LLM.chat import Chat, make_user_message
from speech_to_speech.LLM.responses_api_language_model import ResponsesApiModelHandler
from speech_to_speech.pipeline.messages import (
    EndOfResponse,
    GenerateResponseRequest,
    LLMResponseChunk,
)

from vermittler.proxy import Einstellung, starte_server

BERICHT = "[Zustand] Reachy ist müde und eher zurückhaltend."
BEWEGUNG = frozenset({"dance", "move_head"})
# Tools nachgebildet nach der Conversation App; Namen und Schemata nicht im Pollen-Code geprüft.
TOOLS = [
    {"type": "function", "name": "move_head", "description": "Kopf bewegen",
     "parameters": {"type": "object", "properties": {"direction": {"type": "string"}}, "required": ["direction"]}},
    {"type": "function", "name": "dance", "description": "Einen Tanz abspielen",
     "parameters": {"type": "object", "properties": {"move": {"type": "string"}}}},
    {"type": "function", "name": "camera", "description": "Ein Bild aufnehmen und beschreiben",
     "parameters": {"type": "object", "properties": {"question": {"type": "string"}}}},
    {"type": "function", "name": "do_nothing", "description": "Nichts tun",
     "parameters": {"type": "object", "properties": {}}},
]
ATTRAPPE, PROXY = 8090, 8091


def baue_anfrage() -> GenerateResponseRequest:
    """Gespräch mit Verlauf und einem erledigten Tool-Aufruf, jedes Mal gleich."""
    sitzung = RealtimeSessionCreateRequest(
        type="realtime", instructions="Du bist Reachy, ein freundlicher Roboter. Sprich Deutsch.",
        tools=TOOLS, tool_choice="auto")
    chat = Chat(20)
    chat.add_item(make_user_message("Hallo Reachy, schau mal nach links."))
    chat.add_item(RealtimeConversationItemFunctionCall(
        id="fc_001", type="function_call", call_id="call_001", name="move_head",
        arguments='{"direction": "left"}', status="completed"))
    chat.add_item(RealtimeConversationItemFunctionCallOutput(
        id="fco_001", type="function_call_output", call_id="call_001", output='{"status": "ok"}'))
    chat.add_item(RealtimeConversationItemAssistantMessage(
        id="msg_001", type="message", role="assistant", status="completed",
        content=[{"type": "output_text", "text": "Ich schaue nach links."}]))
    chat.add_item(make_user_message("Kannst du für mich tanzen?"))
    return GenerateResponseRequest(runtime_config=RuntimeConfig(chat=chat, session=sitzung))


def neuer_handler(port: int) -> ResponsesApiModelHandler:
    handler = object.__new__(ResponsesApiModelHandler)
    # setup() wie in speech-to-speech; ruft warmup() auf (Anfrage ohne Streaming).
    ResponsesApiModelHandler.setup(
        handler, model_name="attrappe", base_url=f"http://127.0.0.1:{port}/v1",
        stream=True, disable_thinking=True, reasoning_effort="none", stream_batch_sentences=1)
    return handler


def lauf(port: int) -> dict:
    handler = neuer_handler(port)
    start = time.perf_counter()
    stuecke, tools, fehler = [], [], None
    for ausgabe in handler.process(baue_anfrage()):
        if isinstance(ausgabe, EndOfResponse):
            fehler = ausgabe.error
        elif isinstance(ausgabe, LLMResponseChunk):
            if ausgabe.text:
                stuecke.append((round(time.perf_counter() - start, 2), ausgabe.text))
            tools += [t.name for t in ausgabe.tools]
    return {"stuecke": stuecke, "tools": tools, "fehler": fehler}


def starte(server) -> None:
    threading.Thread(target=server.serve_forever, daemon=True).start()


def mit_proxy(einstellung: Einstellung, aufzeichnung) -> tuple[dict, list[dict]]:
    server = starte_server(PROXY, einstellung)
    starte(server)
    vorher = len(aufzeichnung.anfragen)
    try:
        ergebnis = lauf(PROXY)
    finally:
        server.shutdown()
        server.server_close()
    return ergebnis, aufzeichnung.anfragen[vorher:]


def streaming_geprueft(ergebnis: dict, tool: str | None) -> str:
    zeiten = [t for t, _ in ergebnis["stuecke"]]
    abstaende = [b - a for a, b in itertools.pairwise(zeiten)]
    gestaffelt = len(zeiten) >= 3 and min(abstaende) >= 0.2
    tool_ok = ergebnis["tools"] == ([tool] if tool else [])
    ok = gestaffelt and tool_ok and ergebnis["fehler"] is None
    return (f"{'OK' if ok else 'FEHLER'}: {len(zeiten)} Textstücke bei {zeiten} s, "
            f"Tool-Aufrufe {ergebnis['tools']}, Fehler {ergebnis['fehler']}")


def kopf_ohne_host(anfrage: dict) -> dict:
    return {k.lower(): v for k, v in anfrage["kopf"].items() if k.lower() != "host"}


def pruefe_durchreichen(ref: list[dict], neu: list[dict]) -> list[str]:
    zeilen = []
    for name, a, b in zip(["Aufwärmen (ohne Streaming)", "Antwort (Streaming)"], ref, neu, strict=True):
        gleich_koerper = a["koerper"] == b["koerper"]
        unterschiede = {k for k in kopf_ohne_host(a).keys() | kopf_ohne_host(b).keys()
                        if kopf_ohne_host(a).get(k) != kopf_ohne_host(b).get(k)}
        zeilen.append(f"{name}: Körper byte-gleich: {gleich_koerper}; abweichende Kopfzeilen: {sorted(unterschiede)}")
    return zeilen


def pruefe_bericht(ref: dict, neu: dict, art: str) -> str:
    a, b = json.loads(ref["koerper"]), json.loads(neu["koerper"])
    rest_gleich = {k: v for k, v in a.items() if k != "input"} == {k: v for k, v in b.items() if k != "input"}
    if art == "eintrag":
        ok = b["input"][:-1] == a["input"] and b["input"][-1]["content"][0]["text"] == BERICHT
        stelle = f"letzter Eintrag: {json.dumps(b['input'][-1], ensure_ascii=False)}"
    else:
        letzte_a, letzte_b = a["input"][-1], b["input"][-1]
        ok = (b["input"][:-1] == a["input"][:-1] and letzte_b["content"][:-1] == letzte_a["content"]
              and letzte_b["content"][-1]["text"] == BERICHT)
        stelle = f"letzte Nutzer-Nachricht: {json.dumps(letzte_b, ensure_ascii=False)}"
    n = len(a["input"]) if art == "eintrag" else len(a["input"]) - 1
    anfang_gleich = json.dumps(b["input"][:n]) == json.dumps(a["input"][:n])
    return (f"{'OK' if ok and rest_gleich else 'FEHLER'}: übrige Felder gleich: {rest_gleich}, "
            f"Anfang von input unverändert: {anfang_gleich}; {stelle}")


def pruefe_tools(ref: dict, neu: dict) -> str:
    a, b = json.loads(ref["koerper"]), json.loads(neu["koerper"])
    erwartet = [t for t in a["tools"] if t["name"] not in BEWEGUNG]
    rest_gleich = {k: v for k, v in a.items() if k != "tools"} == {k: v for k, v in b.items() if k != "tools"}
    ok = b["tools"] == erwartet and rest_gleich
    return (f"{'OK' if ok else 'FEHLER'}: vorher {[t['name'] for t in a['tools']]}, "
            f"nachher {[t['name'] for t in b['tools']]}, übrige Felder gleich: {rest_gleich}")


def pruefe_abbruch(aufzeichnung) -> str:
    """Wie speech-to-speech bei einer verworfenen Vorab-Anfrage: Strom mitten drin schließen."""
    server = starte_server(PROXY, Einstellung(ziel=f"http://127.0.0.1:{ATTRAPPE}"))
    starte(server)
    try:
        anfrage = json.loads(aufzeichnung.anfragen[-1]["koerper"])
        client = OpenAI(api_key="none", base_url=f"http://127.0.0.1:{PROXY}/v1")
        anfrage.pop("stream", None)
        strom = client.responses.create(**anfrage, stream=True)
        for ereignis in strom:
            if ereignis.type == "response.output_text.delta":
                break
        vorher = aufzeichnung.abbrueche
        strom.close()
        time.sleep(1.5)
        abgebrochen = aufzeichnung.abbrueche - vorher
        danach = lauf(PROXY)
    finally:
        server.shutdown()
        server.server_close()
    ok = abgebrochen == 1 and danach["fehler"] is None
    return (f"{'OK' if ok else 'FEHLER'}: Attrappe hat {abgebrochen} abgebrochenen Strom bemerkt; "
            f"nächste Anfrage über denselben Proxy-Prozess: {len(danach['stuecke'])} Stücke, Fehler {danach['fehler']}")


def main() -> None:
    server, aufzeichnung = starte_attrappe(ATTRAPPE)
    starte(server)
    ziel = f"http://127.0.0.1:{ATTRAPPE}"
    print("## Lauf", time.strftime("%Y-%m-%d %H:%M:%S"), "\n")
    ref = lauf(ATTRAPPE)
    ref_anfragen = list(aufzeichnung.anfragen)
    print("### 0 Ohne Vermittler (Vergleich)\n-", streaming_geprueft(ref, "move_head"), "\n")
    durch, anfragen = mit_proxy(Einstellung(ziel=ziel), aufzeichnung)
    print("### 1 Durchreichen ohne Änderung")
    for zeile in [*pruefe_durchreichen(ref_anfragen, anfragen), streaming_geprueft(durch, "move_head")]:
        print("-", zeile)
    for art in ("eintrag", "nutzer"):
        ergebnis, anfragen = mit_proxy(Einstellung(ziel=ziel, bericht=BERICHT, bericht_art=art), aufzeichnung)
        print(f"\n### 2 Bericht anhängen, Variante {art}")
        print("-", pruefe_bericht(ref_anfragen[1], anfragen[1], art))
        print("-", streaming_geprueft(ergebnis, "move_head"))
        print("- Aufwärm-Anfrage ebenfalls verändert:", anfragen[0]["koerper"] != ref_anfragen[0]["koerper"])
    ergebnis, anfragen = mit_proxy(Einstellung(ziel=ziel, ohne_tools=BEWEGUNG), aufzeichnung)
    print("\n### 3 Tools entfernen", sorted(BEWEGUNG))
    print("-", pruefe_tools(ref_anfragen[1], anfragen[1]))
    print("-", streaming_geprueft(ergebnis, "camera"))
    print("\n### 4 Abbruch mitten im Strom\n-", pruefe_abbruch(aufzeichnung))
    print("\n### Gesendete Anfrage (Streaming, ohne Vermittler)\n```json")
    print(json.dumps(json.loads(ref_anfragen[1]["koerper"]), ensure_ascii=False, indent=1))
    print("```")


if __name__ == "__main__":
    main()
