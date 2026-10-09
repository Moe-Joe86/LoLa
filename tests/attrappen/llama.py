"""Attrappe für llama.cpp: merkt sich Anfragen, antwortet auf `/v1/responses` als Strom oder am Stück.

Der Strom kommt in Stücken mit Pausen, damit Tests sehen, ob der Vermittler sofort weiterreicht.
Bricht der Aufrufer ab, merkt sich die Attrappe, wie lange nach Beginn der Anfrage sie das bemerkt hat.
"""

import json
import select
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STUECKE = ["Hallo", " ich", " bin", " LoLa."]


class LlamaAttrappe(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, pause: float = 0.1, vorlauf: float = 0.0) -> None:
        super().__init__(("127.0.0.1", 0), _Behandler)
        self.pause = pause  # Pause zwischen den Stücken des Stroms
        self.vorlauf = vorlauf  # Wartezeit vor dem ersten Stück (das Modell „denkt“)
        self.anfragen: list[tuple[str, str, dict, bytes]] = []
        self.abbruch_bemerkt_nach: float | None = None
        threading.Thread(target=self.serve_forever, daemon=True).start()

    @property
    def port(self) -> int:
        return self.server_address[1]


class _Behandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server: LlamaAttrappe

    def _weg(self) -> bool:
        lesbar, _, _ = select.select([self.connection], [], [], 0)
        return bool(lesbar) and self.connection.recv(1, socket.MSG_PEEK) == b""

    def _warte(self, dauer: float, beginn: float) -> bool:
        """Wartet und gibt False zurück, sobald der Aufrufer weg ist."""
        ende = time.monotonic() + dauer
        while time.monotonic() < ende:
            if self._weg():
                self.server.abbruch_bemerkt_nach = time.monotonic() - beginn
                return False
            time.sleep(0.01)
        return True

    def _antworte(self) -> None:
        beginn = time.monotonic()
        roh = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        self.server.anfragen.append((self.command, self.path, dict(self.headers), roh))
        if self.path == "/health":
            self._am_stueck(200, b'{"status":"ok"}')
        elif self.path != "/v1/responses":
            self._am_stueck(404, b'{"error":"unbekannt"}')
        elif not json.loads(roh).get("stream"):
            self._am_stueck(200, json.dumps({"output_text": "".join(STUECKE)}).encode())
        else:
            self._strom(beginn)

    do_GET = do_POST = _antworte

    def _am_stueck(self, status: int, koerper: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Attrappe", "ja")
        self.send_header("Content-Length", str(len(koerper)))
        self.end_headers()
        self.wfile.write(koerper)

    def _strom(self, beginn: float) -> None:
        if not self._warte(self.server.vorlauf, beginn):
            self.close_connection = True
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        try:
            for stueck in STUECKE:
                ereignis = {"type": "response.output_text.delta", "delta": stueck}
                daten = f"event: {ereignis['type']}\ndata: {json.dumps(ereignis)}\n\n".encode()
                self.wfile.write(f"{len(daten):x}\r\n".encode() + daten + b"\r\n")
                self.wfile.flush()
                if not self._warte(self.server.pause, beginn):
                    self.close_connection = True
                    return
            self.wfile.write(b"0\r\n\r\n")
        except OSError:
            self.server.abbruch_bemerkt_nach = time.monotonic() - beginn
            self.close_connection = True

    def log_message(self, *args) -> None:
        pass
