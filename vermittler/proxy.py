"""Vermittler: HTTP-Proxy zwischen speech-to-speech und llama.cpp. Nur Standardbibliothek.

Er setzt in Gesprächsanfragen an `/v1/responses` den Zustandsbericht vor den letzten Nutzersatz, entfernt
gesperrte Tools und schreibt das Anfrage-Log. Alles andere reicht er unverändert durch, Antworten Stück
für Stück. Schließt der Aufrufer die Verbindung, schließt der Vermittler die zu llama.cpp sofort.

Aufruf: uv run python -m vermittler.proxy [eigener Port] [Port von llama.cpp]
"""

import http.client
import select
import socket
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from seele.charakter import charakter_laden
from seele.erklaer_log import ErklaerLog
from seele.zustand import grundzustand
from seele.zustandsbericht import zustandsbericht
from vermittler.anfrage import Aenderung, bearbeite, setzt_fort
from vermittler.anfrage_log import AnfrageLog, frist_tage

# Diese Kopfzeilen gelten nur für eine einzelne Verbindung und werden nicht weitergereicht.
NUR_EINE_STRECKE = {"connection", "keep-alive", "transfer-encoding", "content-length", "host", "te", "upgrade"}
WARTEZEIT_S = 600


@dataclass
class Einstellung:
    ziel: tuple[str, int]
    bericht: Callable[[], str]
    log: AnfrageLog
    gesperrte_tools: Callable[[], frozenset[str]] = frozenset
    letzter_satz: str = ""


class Vermittler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    einstellung: Einstellung

    def _reiche_weiter(self) -> None:
        beginn = time.monotonic()
        roh = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        aenderung = Aenderung()
        if self.command == "POST" and self.path.split("?")[0].endswith("/responses"):
            e = self.einstellung
            roh, aenderung = bearbeite(roh, e.bericht(), e.gesperrte_tools())
        kopf = {name: wert for name, wert in self.headers.items() if name.lower() not in NUR_EINE_STRECKE}
        ziel = http.client.HTTPConnection(*self.einstellung.ziel, timeout=WARTEZEIT_S)
        fertig = threading.Event()
        abgebrochen = False
        try:
            ziel.request(self.command, self.path, body=roh or None, headers=kopf)
            threading.Thread(target=self._wache, args=(ziel, fertig), daemon=True).start()
            antwort = ziel.getresponse()
            self._sende_antwort(antwort)
        except (BrokenPipeError, ConnectionResetError, http.client.HTTPException, OSError) as fehler:
            abgebrochen = self._aufrufer_ist_weg()
            if not abgebrochen:
                self._melde_fehler(fehler)
            self.close_connection = True
        finally:
            fertig.set()
            ziel.close()
        if aenderung.gesagt:
            self._schreibe_log(aenderung, (time.monotonic() - beginn) * 1000, abgebrochen)

    do_GET = do_POST = do_PUT = do_DELETE = _reiche_weiter

    def _sende_antwort(self, antwort: http.client.HTTPResponse) -> None:
        self.send_response(antwort.status, antwort.reason)
        for name, wert in antwort.getheaders():
            if name.lower() not in NUR_EINE_STRECKE:
                self.send_header(name, wert)
        laenge = antwort.getheader("Content-Length")
        if laenge is not None:
            self.send_header("Content-Length", laenge)
            self.end_headers()
            self.wfile.write(antwort.read())
            return
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        while stueck := antwort.read1(65536):  # liefert, was da ist, und wartet nicht auf volle Größe
            self.wfile.write(f"{len(stueck):x}\r\n".encode() + stueck + b"\r\n")
            self.wfile.flush()
        self.wfile.write(b"0\r\n\r\n")

    def _aufrufer_ist_weg(self) -> bool:
        """Wahr, wenn der Aufrufer seine Seite geschlossen hat (ohne etwas zu verbrauchen)."""
        try:
            lesbar, _, _ = select.select([self.connection], [], [], 0)
            return bool(lesbar) and self.connection.recv(1, socket.MSG_PEEK) == b""
        except OSError:
            return True

    def _wache(self, ziel: http.client.HTTPConnection, fertig: threading.Event) -> None:
        """Schließt die Verbindung zu llama.cpp, sobald der Aufrufer weg ist, auch vor dem ersten Wort."""
        while not fertig.wait(0.05):
            if self._aufrufer_ist_weg():
                if ziel.sock is not None:
                    ziel.sock.shutdown(socket.SHUT_RDWR)
                return

    def _melde_fehler(self, fehler: Exception) -> None:
        text = f'{{"error": "Vermittler erreicht llama.cpp nicht: {type(fehler).__name__}"}}'.encode()
        try:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(text)))
            self.end_headers()
            self.wfile.write(text)
        except OSError:
            pass

    def _schreibe_log(self, aenderung: Aenderung, dauer_ms: float, abgebrochen: bool) -> None:
        e = self.einstellung
        wiederholt = setzt_fort(e.letzter_satz, aenderung.gesagt)
        e.letzter_satz = aenderung.gesagt
        a = aenderung
        e.log.schreiben(a.gesagt, a.bericht, a.entfernte_tools, dauer_ms, wiederholt, abgebrochen)

    def log_message(self, *args) -> None:
        """Kein Zugriffslog auf der Konsole: Was zählt, steht im Anfrage-Log."""


def baue_server(port: int, einstellung: Einstellung) -> ThreadingHTTPServer:
    """Baut den Server und räumt dabei alte Anfrage-Logs weg. Gestartet wird er mit `serve_forever`."""
    einstellung.log.aufraeumen()
    behandler = type("VermittlerMitEinstellung", (Vermittler,), {"einstellung": einstellung})
    server = ThreadingHTTPServer(("127.0.0.1", port), behandler)
    server.daemon_threads = True
    return server


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8091
    ziel_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8090
    daten = Path("daten")
    charakter = charakter_laden()
    bericht = zustandsbericht(charakter, grundzustand(charakter, ErklaerLog(datei=daten / "erklaer-log.jsonl")))
    log = AnfrageLog(daten, frist=frist_tage())
    server = baue_server(port, Einstellung(("127.0.0.1", ziel_port), lambda: bericht, log))
    print(f"Vermittler lauscht auf 127.0.0.1:{port} und gibt an 127.0.0.1:{ziel_port} weiter.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
