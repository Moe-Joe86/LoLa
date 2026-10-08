"""Machbarkeitstest A2: Vermittler als HTTP-Proxy zwischen speech-to-speech und llama.cpp.

Nur Standardbibliothek. Reicht jede Anfrage an das Ziel weiter. Bei POST auf
.../responses kann er wahlweise einen Bericht anhängen und Tools entfernen.
Die Antwort geht Stück für Stück zurück, ohne Sammeln, damit Streaming erhalten bleibt.
"""

import argparse
import http.client
import json
import logging
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

logger = logging.getLogger("vermittler")

# Kopfzeilen, die nur für eine einzelne Verbindung gelten und nicht weitergereicht werden.
NUR_FUER_DIESE_VERBINDUNG = {
    "connection", "keep-alive", "proxy-connection", "transfer-encoding",
    "te", "trailer", "upgrade", "host", "content-length",
}


@dataclass
class Einstellung:
    ziel: str = "http://127.0.0.1:8080"
    bericht: str | None = None
    bericht_art: str = "eintrag"  # "eintrag": letzter Eintrag in input; "nutzer": an letzte Nutzer-Nachricht
    ohne_tools: frozenset[str] = field(default_factory=frozenset)


def bericht_anhaengen(anfrage: dict, bericht: str, art: str) -> None:
    eingabe = anfrage.get("input")
    if not isinstance(eingabe, list):
        return
    if art == "eintrag":
        eingabe.append({
            "type": "message",
            "role": "system",
            "content": [{"type": "input_text", "text": bericht}],
        })
        return
    for eintrag in reversed(eingabe):
        if eintrag.get("type", "message") == "message" and eintrag.get("role") == "user":
            inhalt = eintrag.get("content")
            if isinstance(inhalt, str):
                eintrag["content"] = inhalt + "\n\n" + bericht
            else:
                inhalt.append({"type": "input_text", "text": bericht})
            return


def tools_entfernen(anfrage: dict, namen: frozenset[str]) -> list[str]:
    tools = anfrage.get("tools")
    if not tools:
        return []
    behalten = [t for t in tools if t.get("name") not in namen]
    entfernt = [t.get("name") for t in tools if t.get("name") in namen]
    wahl = anfrage.get("tool_choice")
    if isinstance(wahl, dict) and wahl.get("name") in namen:
        anfrage["tool_choice"] = "auto"
    if behalten:
        anfrage["tools"] = behalten
    else:
        anfrage.pop("tools", None)
        anfrage.pop("tool_choice", None)
    return entfernt


def anfrage_anpassen(pfad: str, koerper: bytes, einstellung: Einstellung) -> bytes:
    """Gibt den Körper unverändert zurück, wenn nichts zu tun ist (byte-genau)."""
    if not pfad.rstrip("/").endswith("/responses"):
        return koerper
    if einstellung.bericht is None and not einstellung.ohne_tools:
        return koerper
    anfrage = json.loads(koerper)
    entfernt = tools_entfernen(anfrage, einstellung.ohne_tools)
    if einstellung.bericht is not None:
        bericht_anhaengen(anfrage, einstellung.bericht, einstellung.bericht_art)
    logger.info("angepasst: bericht=%s entfernt=%s", einstellung.bericht_art if einstellung.bericht else "-", entfernt)
    return json.dumps(anfrage, ensure_ascii=False).encode("utf-8")


class VermittlerHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    einstellung: Einstellung  # wird pro Server gesetzt

    def do_GET(self) -> None:
        self._weiterreichen()

    def do_POST(self) -> None:
        self._weiterreichen()

    def log_message(self, format: str, *args) -> None:
        logger.debug(format, *args)

    def _weiterreichen(self) -> None:
        laenge = int(self.headers.get("Content-Length", 0))
        koerper = self.rfile.read(laenge) if laenge else b""
        if self.command == "POST":
            koerper = anfrage_anpassen(self.path, koerper, self.einstellung)
        ziel = urlsplit(self.einstellung.ziel)
        verbindung = http.client.HTTPConnection(ziel.hostname, ziel.port, timeout=60)
        try:
            kopf = {k: v for k, v in self.headers.items() if k.lower() not in NUR_FUER_DIESE_VERBINDUNG}
            kopf["Content-Length"] = str(len(koerper))
            verbindung.request(self.command, self.path, body=koerper, headers=kopf)
            antwort = verbindung.getresponse()
            self._antwort_zurueck(antwort)
        except (BrokenPipeError, ConnectionResetError):
            logger.info("Aufrufer hat die Verbindung geschlossen, Ziel-Verbindung wird beendet")
            self.close_connection = True
        finally:
            verbindung.close()

    def _antwort_zurueck(self, antwort: http.client.HTTPResponse) -> None:
        self.send_response(antwort.status, antwort.reason)
        for k, v in antwort.getheaders():
            if k.lower() not in NUR_FUER_DIESE_VERBINDUNG:
                self.send_header(k, v)
        laenge = antwort.getheader("Content-Length")
        if laenge is not None:
            self.send_header("Content-Length", laenge)
            self.end_headers()
            self.wfile.write(antwort.read())
            return
        # Unbekannte Länge (Streaming): Stück für Stück in Chunked-Kodierung weitergeben.
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        while stueck := antwort.read1(65536):
            self.wfile.write(b"%x\r\n%s\r\n" % (len(stueck), stueck))
            self.wfile.flush()
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()


def starte_server(port: int, einstellung: Einstellung) -> ThreadingHTTPServer:
    handler = type("Handler", (VermittlerHandler,), {"einstellung": einstellung})
    return ThreadingHTTPServer(("127.0.0.1", port), handler)


def main() -> None:
    teiler = argparse.ArgumentParser(description="Vermittler (Machbarkeitstest A2)")
    teiler.add_argument("--port", type=int, default=8081)
    teiler.add_argument("--ziel", default="http://127.0.0.1:8080")
    teiler.add_argument("--bericht")
    teiler.add_argument("--bericht-art", choices=["eintrag", "nutzer"], default="eintrag")
    teiler.add_argument("--ohne-tool", action="append", default=[])
    argumente = teiler.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    einstellung = Einstellung(argumente.ziel, argumente.bericht, argumente.bericht_art, frozenset(argumente.ohne_tool))
    starte_server(argumente.port, einstellung).serve_forever()


if __name__ == "__main__":
    main()
