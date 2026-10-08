"""Attrappe für llama.cpp: beantwortet POST /v1/responses mit einer festen Antwort.

Jede empfangene Anfrage wird mit Kopfzeilen und Körper (Bytes) gespeichert.
Mit stream=true kommen die Ereignisse einzeln mit Pause, damit sich prüfen lässt,
ob der Vermittler sie stückweise weiterreicht. Wenn die Anfrage Tools enthält,
ruft die Antwort zusätzlich das erste davon auf.
Die Ereignisfolge folgt dem OpenAI-Format; ob llama.cpp genau so sendet, ist ungeprüft.
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SAETZE = ["Hallo Patrick. ", "Schön, dich zu hören. ", "Ich tanze gleich für dich. ", "Los geht's! "]
PAUSE_S = 0.3


class Aufzeichnung:
    def __init__(self) -> None:
        self.anfragen: list[dict] = []
        self.abbrueche = 0
        self.sperre = threading.Lock()

    def merken(self, kopf: dict, koerper: bytes) -> None:
        with self.sperre:
            self.anfragen.append({"kopf": kopf, "koerper": koerper})


def _antwort_objekt(ausgabe: list[dict], status: str) -> dict:
    return {
        "id": "resp_attrappe", "object": "response", "created_at": int(time.time()),
        "model": "attrappe", "status": status, "output": ausgabe,
        "parallel_tool_calls": False, "tool_choice": "auto", "tools": [],
        "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120,
                  "input_tokens_details": {"cached_tokens": 0},
                  "output_tokens_details": {"reasoning_tokens": 0}},
    }


def _nachricht(text: str, status: str = "completed") -> dict:
    return {"type": "message", "id": "msg_attrappe", "role": "assistant", "status": status,
            "content": [{"type": "output_text", "text": text, "annotations": []}]}


def _tool_aufruf(name: str) -> dict:
    return {"type": "function_call", "id": "fc_attrappe", "call_id": "call_attrappe",
            "name": name, "arguments": "{}", "status": "completed"}


def _ereignisse(tool_name: str | None):
    """Liefert (Ereignis, Pause davor) in der Reihenfolge der Responses API."""
    text = "".join(SAETZE)
    yield {"type": "response.created", "response": _antwort_objekt([], "in_progress")}, 0
    yield {"type": "response.output_item.added", "output_index": 0, "item": _nachricht("", "in_progress")}, 0
    for satz in SAETZE:
        yield {"type": "response.output_text.delta", "item_id": "msg_attrappe", "output_index": 0,
               "content_index": 0, "delta": satz, "logprobs": []}, PAUSE_S
    yield {"type": "response.output_text.done", "item_id": "msg_attrappe", "output_index": 0,
           "content_index": 0, "text": text, "logprobs": []}, 0
    ausgabe = [_nachricht(text)]
    yield {"type": "response.output_item.done", "output_index": 0, "item": ausgabe[0]}, 0
    if tool_name:
        ausgabe.append(_tool_aufruf(tool_name))
        yield {"type": "response.output_item.done", "output_index": 1, "item": ausgabe[1]}, PAUSE_S
    yield {"type": "response.completed", "response": _antwort_objekt(ausgabe, "completed")}, 0


class AttrappenHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    aufzeichnung: Aufzeichnung

    def log_message(self, format: str, *args) -> None:
        pass

    def do_POST(self) -> None:
        koerper = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.aufzeichnung.merken(dict(self.headers.items()), koerper)
        anfrage = json.loads(koerper)
        tools = anfrage.get("tools") or []
        tool_name = tools[0]["name"] if tools else None
        if anfrage.get("stream"):
            self._streamen(tool_name)
        else:
            self._ganz_senden(tool_name)

    def _ganz_senden(self, tool_name: str | None) -> None:
        ausgabe = [_nachricht("".join(SAETZE))] + ([_tool_aufruf(tool_name)] if tool_name else [])
        daten = json.dumps(_antwort_objekt(ausgabe, "completed")).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(daten)))
        self.end_headers()
        self.wfile.write(daten)

    def _streamen(self, tool_name: str | None) -> None:
        # Wie llama-server: Server-Sent Events in Chunked-Kodierung.
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        try:
            for ereignis, pause in _ereignisse(tool_name):
                time.sleep(pause)
                zeile = f"event: {ereignis['type']}\ndata: {json.dumps(ereignis)}\n\n".encode()
                self.wfile.write(b"%x\r\n%s\r\n" % (len(zeile), zeile))
                self.wfile.flush()
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            with self.aufzeichnung.sperre:
                self.aufzeichnung.abbrueche += 1
            self.close_connection = True


def starte_attrappe(port: int) -> tuple[ThreadingHTTPServer, Aufzeichnung]:
    aufzeichnung = Aufzeichnung()
    handler = type("Handler", (AttrappenHandler,), {"aufzeichnung": aufzeichnung})
    return ThreadingHTTPServer(("127.0.0.1", port), handler), aufzeichnung
