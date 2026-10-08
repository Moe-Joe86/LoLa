"""A3: gemeinsame Bausteine der Messskripte. Wird nie gemergt.

Die Anfrage baut der echte Handler aus speech-to-speech (Commit 8024ccf), damit dessen englischer
Rahmentext enthalten ist. Tools und Standardprofil werden zur Laufzeit aus dem Klon der Conversation
App gelesen (nur lesen, nichts kopiert). Den Bericht hängt die Funktion des Proxys aus test/vermittler an.
Umgebung wie in A1: PYTHONPATH=<test/vermittler>:<test/vermittler>/tests, NLTK_DATA, llama-server auf 8090.
"""

import ast
import copy
import json
import re
import threading
import time
import urllib.request
from pathlib import Path

from attrappen.llama_attrappe import starte_attrappe
from openai.types.realtime import RealtimeSessionCreateRequest
from openai.types.realtime.conversation_item import (
    RealtimeConversationItemAssistantMessage,
    RealtimeConversationItemFunctionCall,
    RealtimeConversationItemFunctionCallOutput,
)
from speech_to_speech.api.openai_realtime.runtime_config import RuntimeConfig
from speech_to_speech.LLM.chat import Chat, make_user_message
from speech_to_speech.LLM.responses_api_language_model import ResponsesApiModelHandler
from speech_to_speech.pipeline.messages import GenerateResponseRequest
from vermittler.proxy import bericht_anhaengen

LLAMA, ATTRAPPE = 8090, 8092
HIER = Path(__file__).parent
APP = Path.home() / "lola-laufzeit" / "reachy_mini_conversation_app"
ERGEBNISSE = Path.home() / "lola-laufzeit" / "messung" / "a3"
TOOL_NAMEN = ["dance", "stop_dance", "play_emotion", "move_head", "camera",
              "idle_do_nothing", "go_to_sleep", "sweep_look", "head_tracking"]
SAETZE = [z.strip() for z in (HIER / "testsaetze.txt").read_text(encoding="utf-8").splitlines() if z.strip()]
PLATZHALTER = "PLATZHALTER"

MUSTERZEILE = "- For expression/background tools, speak first."  # Anfang der Zeile im Rahmen von speech-to-speech
ERSATZZEILE = "- For expression, motion and other physical tools, call the tool immediately without speaking first."

DEUTSCH = set("ich du der die das ist nicht und ein eine mir dir bin kann wie was ja nein gerne es zu auf für "
              "mit dich mich habe hast wir sie aber auch noch schon gut klar leider bitte danke hallo den dem "
              "heute dann wenn oder nur sehr mal los geht's kein keine weiß tut leid".split())
ENGLISCH = set("the you i'm here's sure is are my what how can i it's that this your have not and to of a "
               "for with best dance let's i'll don't sorry please thanks there will be me heard make ready".split())


def profil_text(datei: Path) -> str:
    """Anweisungstext eines Profils: alles hinter dem zweiten +++."""
    return datei.read_text(encoding="utf-8").split("+++", 2)[2].strip()


def anweisungen() -> dict[str, str]:
    deutsch = profil_text(HIER / "profil" / "reachy_deutsch" / "profile.md")
    return {
        "app_standard": profil_text(APP / "profiles" / "default" / "profile.md"),
        "deutsch_kurz": "Du bist Reachy, ein freundlicher Roboter. Sprich Deutsch. Antworte kurz.",
        "deutsch_profil": deutsch,
        "deutsch_profil_regel": deutsch + "\n" + (HIER / "zustandsregel.md").read_text(encoding="utf-8").rstrip(),
    }


def lade_tools() -> list[dict]:
    """Liest Name, Beschreibung und Schema der Tools aus dem Quelltext der App, ohne ihn auszuführen."""
    emotionen = []
    tools = []
    for name in TOOL_NAMEN:
        baum = ast.parse((APP / "src" / "reachy_mini_conversation_app" / "tools" / f"{name}.py").read_text())
        felder = {}
        for knoten in ast.walk(baum):
            if isinstance(knoten, ast.AnnAssign) and getattr(knoten.target, "id", "") == "EMOTION_INTENTS":
                emotionen = list(ast.literal_eval(knoten.value))
            if not isinstance(knoten, ast.Assign) or not isinstance(knoten.targets[0], ast.Name):
                continue
            ziel = knoten.targets[0].id
            if ziel in ("name", "description", "parameters_schema"):
                try:
                    felder[ziel] = ast.literal_eval(knoten.value)
                except ValueError:
                    felder.setdefault(ziel, None)
        if name == "dance":  # Liste der Tänze entsteht erst zur Laufzeit der App, hier vereinfacht
            felder["parameters_schema"] = {"type": "object", "required": [], "properties": {
                "move": {"type": "string", "description": "Name of the move; omit for random."},
                "repeat": {"type": "integer", "description": "How many times to repeat the move (default 1)."}}}
        if name == "play_emotion":
            felder["parameters_schema"] = {"type": "object", "required": [], "properties": {
                "emotion": {"type": "string", "enum": emotionen,
                            "description": "Compact emotional intent to express."}}}
        tools.append({"type": "function", "name": felder["name"], "description": felder["description"],
                      "parameters": felder["parameters_schema"]})
    return tools


def baue_anfrage(anweisung: str, tools: list[dict], verlauf: bool = False, sprachhinweis: bool = False) -> dict:
    """Echter Handler läuft einmal gegen die Attrappe; zurück kommt seine Streaming-Anfrage."""
    server, aufzeichnung = starte_attrappe(ATTRAPPE)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    handler = object.__new__(ResponsesApiModelHandler)
    ResponsesApiModelHandler.setup(
        handler, model_name="qwen3", base_url=f"http://127.0.0.1:{ATTRAPPE}/v1", stream=True,
        disable_thinking=True, reasoning_effort="none", stream_batch_sentences=1, enable_lang_prompt=sprachhinweis)
    chat = Chat(20)
    if verlauf:
        chat.add_item(make_user_message("Hallo Reachy, schau mal nach links."))
        chat.add_item(RealtimeConversationItemFunctionCall(
            id="fc_001", type="function_call", call_id="call_001", name="move_head",
            arguments='{"direction": "left"}', status="completed"))
        chat.add_item(RealtimeConversationItemFunctionCallOutput(
            id="fco_001", type="function_call_output", call_id="call_001", output='{"status": "ok"}'))
        chat.add_item(RealtimeConversationItemAssistantMessage(
            id="msg_001", type="message", role="assistant", status="completed",
            content=[{"type": "output_text", "text": "Ich schaue nach links."}]))
        chat.add_item(make_user_message("Danke. Und wie heißt du?"))
        chat.add_item(RealtimeConversationItemAssistantMessage(
            id="msg_002", type="message", role="assistant", status="completed",
            content=[{"type": "output_text", "text": "Ich heiße Reachy."}]))
    chat.add_item(make_user_message(PLATZHALTER))
    sitzung = RealtimeSessionCreateRequest(type="realtime", instructions=anweisung, tools=tools, tool_choice="auto")
    list(handler.process(GenerateResponseRequest(
        runtime_config=RuntimeConfig(chat=chat, session=sitzung), language_code="de")))
    server.shutdown()
    server.server_close()
    return json.loads(aufzeichnung.anfragen[-1]["koerper"])


def rahmen_ohne_muster(anfrage: dict) -> dict:
    """Ersetzt im Rahmentext die Zeile mit dem englischen Mustersatz (das müsste der Vermittler tun)."""
    neu = copy.deepcopy(anfrage)
    teil = neu["input"][0]["content"][0]
    zeilen = teil["text"].split("\n")
    treffer = [i for i, z in enumerate(zeilen) if z.startswith(MUSTERZEILE)]
    assert len(treffer) == 1
    zeilen[treffer[0]] = ERSATZZEILE
    teil["text"] = "\n".join(zeilen)
    return neu


def mit_satz(anfrage: dict, satz: str, bericht: str | None = None, position: str = "eintrag") -> dict:
    neu = copy.deepcopy(anfrage)
    letzte = neu["input"][-1]["content"][0]
    assert letzte["text"] == PLATZHALTER
    letzte["text"] = satz
    if bericht and position == "davor":  # Systemeintrag vor dem letzten Nutzersatz; kann der Proxy aus A2 noch nicht
        neu["input"].insert(-1, {"type": "message", "role": "system",
                                 "content": [{"type": "input_text", "text": bericht}]})
    elif bericht:
        bericht_anhaengen(neu, bericht, position)
    return neu


def sende(anfrage: dict) -> dict:
    """Schickt die Anfrage an llama.cpp und sammelt Text und Tool-Aufrufe."""
    daten = json.dumps(anfrage, ensure_ascii=False).encode("utf-8")
    http_anfrage = urllib.request.Request(
        f"http://127.0.0.1:{LLAMA}/v1/responses", daten, {"Content-Type": "application/json"})
    text, tools, start = "", [], time.perf_counter()
    with urllib.request.urlopen(http_anfrage, timeout=120) as antwort:
        for zeile in antwort:
            zeile = zeile.decode("utf-8").strip()
            if not zeile.startswith("data: ") or zeile == "data: [DONE]":
                continue
            ereignis = json.loads(zeile[6:])
            if ereignis.get("type") == "response.output_text.delta":
                text += ereignis["delta"]
            elif (ereignis.get("type") == "response.output_item.done"
                  and ereignis["item"].get("type") == "function_call"):
                tools.append(f"{ereignis['item']['name']}({ereignis['item']['arguments']})")
    return {"text": " ".join(text.split()), "tools": tools, "dauer_s": round(time.perf_counter() - start, 2)}


def sprache(text: str) -> str:
    """Grobe Einordnung über häufige Wörter: deutsch, englisch, gemischt, leer oder unklar."""
    woerter = re.findall(r"[a-zäöüß']+", text.lower())
    if not woerter:
        return "leer"
    d, e = sum(w in DEUTSCH for w in woerter), sum(w in ENGLISCH for w in woerter)
    if any(z in text.lower() for z in "äöüß"):
        d += 1
    if d and e and min(d, e) / max(d, e) > 0.5:
        return "gemischt"
    if d == e:
        return "unklar"
    return "deutsch" if d > e else "englisch"


def speichere(name: str, zeilen: list[dict]) -> Path:
    ERGEBNISSE.mkdir(parents=True, exist_ok=True)
    ziel = ERGEBNISSE / f"{name}.json"
    ziel.write_text(json.dumps(zeilen, ensure_ascii=False, indent=1), encoding="utf-8")
    return ziel
