"""B4: Was kostet der Vermittler? Dieselbe Anfrage abwechselnd direkt an llama.cpp und über den Vermittler.

Direkt geht die Anfrage mit schon eingesetztem Bericht, über den Vermittler ohne: Bei llama.cpp kommt
beide Male derselbe Text an. Gemessen wird die Zeit bis zum ersten Textstück. Auch der Abbruch wird hier gemessen.
Aufruf (im Repo): uv run python tests/b4/zusatzzeit.py [Paare]
"""

import http.client
import json
import statistics
import sys
import time

from rolle_app import lade_tools, profil

from seele.charakter import charakter_laden
from seele.erklaer_log import ErklaerLog
from seele.zustand import grundzustand
from seele.zustandsbericht import zustandsbericht
from vermittler.anfrage import bearbeite

LLAMA, VERMITTLER = 8090, 8091


def anfrage(satz: str, laenge: int = 40, anweisung: str | None = None) -> bytes:
    text, namen = profil()
    text = anweisung or text
    eintraege = [
        {"type": "message", "role": "system", "content": [{"type": "input_text", "text": text}]},
        {"type": "message", "role": "user", "content": [{"type": "input_text", "text": satz}]},
    ]
    koerper = {
        "model": "qwen3",
        "input": eintraege,
        "tools": lade_tools(namen),
        "stream": True,
        "reasoning": {"effort": "none"},
        "max_output_tokens": laenge,
    }
    return json.dumps(koerper, ensure_ascii=False).encode()


def sende(port: int, koerper: bytes, abbruch_nach: float | None = None) -> tuple[float, float]:
    """Gibt die Zeit bis zum ersten Textstück und die Gesamtzeit zurück. `abbruch_nach`: Verbindung dann schließen."""
    verbindung = http.client.HTTPConnection("127.0.0.1", port, timeout=120)
    beginn = time.perf_counter()
    verbindung.request("POST", "/v1/responses", body=koerper, headers={"Content-Type": "application/json"})
    if abbruch_nach is not None and abbruch_nach < 0:  # schon vor der ersten Antwortzeile schließen
        time.sleep(-abbruch_nach)
        verbindung.close()
        return 0.0, time.perf_counter() - beginn
    antwort = verbindung.getresponse()
    erstes = 0.0
    for zeile in antwort:
        if not erstes and b"output_text.delta" in zeile:
            erstes = time.perf_counter() - beginn
            if abbruch_nach is not None:
                time.sleep(abbruch_nach)
                break
    verbindung.close()
    return erstes, time.perf_counter() - beginn


def rechnet_llama() -> bool:
    verbindung = http.client.HTTPConnection("127.0.0.1", LLAMA, timeout=5)
    verbindung.request("GET", "/slots")
    return any(platz.get("is_processing") for platz in json.loads(verbindung.getresponse().read()))


def bis_llama_ruht() -> float:
    beginn = time.perf_counter()
    while rechnet_llama():
        time.sleep(0.005)
    return time.perf_counter() - beginn


def main(paare: int) -> None:
    charakter = charakter_laden()
    bericht = zustandsbericht(charakter, grundzustand(charakter, ErklaerLog()))
    ohne = anfrage("Wie geht es dir heute?")
    mit, _ = bearbeite(ohne, bericht)
    print(f"Anfrage {len(ohne)} Bytes, mit Bericht {len(mit)} Bytes")
    for port, koerper in ((LLAMA, mit), (VERMITTLER, ohne)):  # Zwischenspeicher füllen
        sende(port, koerper)
    direkt, ueber = [], []
    for _ in range(paare):
        direkt.append(sende(LLAMA, mit)[0] * 1000)
        ueber.append(sende(VERMITTLER, ohne)[0] * 1000)
    for name, werte in (("direkt", direkt), ("über den Vermittler", ueber)):
        print(
            f"{name:20}: erstes Textstück Median {statistics.median(werte):.1f} ms, "
            f"Mittel {statistics.mean(werte):.1f} ms, höchstens {max(werte):.1f} ms"
        )
    unterschied = [u - d for u, d in zip(ueber, direkt, strict=True)]
    print(f"Zusatzzeit je Paar: Median {statistics.median(unterschied):.1f} ms, höchstens {max(unterschied):.1f} ms")

    schreiber = "Du bist ein Schriftsteller. Du schreibst immer sehr lange, ausführliche Texte."
    lang = anfrage("Schreib eine Geschichte über einen Drachen, mindestens tausend Wörter.", 1500, schreiber)
    _, volle_dauer = sende(VERMITTLER, lang)
    print(f"Lange Antwort ohne Abbruch: {volle_dauer:.1f} s")
    for name, wann in (("nach dem ersten Textstück", 0.2), ("vor der ersten Antwortzeile", -0.02)):
        for port, weg in ((LLAMA, "direkt"), (VERMITTLER, "Vermittler")):
            for _ in range(3):
                _, dauer = sende(port, lang if port == VERMITTLER else bearbeite(lang, bericht)[0], abbruch_nach=wann)
                rechnete = rechnet_llama()
                print(
                    f"Abbruch {name}, {weg}: geschlossen nach {dauer * 1000:.0f} ms, llama.cpp rechnete da noch: "
                    f"{rechnete}, ruht {bis_llama_ruht() * 1000:.0f} ms später"
                )
                time.sleep(0.3)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
