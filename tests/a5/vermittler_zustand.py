"""Vermittler wie im Betrieb, aber der Zustand kommt aus einer Datei und lässt sich so je Anfrage umschalten
(nur für den Modellvergleich A5). Aufruf im Repo-Ordner: uv run python tests/a5/vermittler_zustand.py

Die Datei ~/lola-laufzeit/messung/a5/zustand.txt enthält „gut“ oder „muede“.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from seele.charakter import charakter_laden  # noqa: E402
from seele.zustand import Zustand  # noqa: E402
from seele.zustandsbericht import zustandsbericht  # noqa: E402
from vermittler.anfrage_log import AnfrageLog  # noqa: E402
from vermittler.proxy import Einstellung, baue_server  # noqa: E402

DATEI = Path.home() / "lola-laufzeit/messung/a5/zustand.txt"
ZUSTAENDE = {  # gut gelaunt und ruhig; „müde und zurückhaltend“ in den Bausteinen unserer Tabelle
    "gut": Zustand(valenz=0.4, erregung=0.4),
    "muede": Zustand(valenz=-0.4, erregung=0.1),
}


def main() -> None:
    charakter = charakter_laden()
    berichte = {name: zustandsbericht(charakter, zustand) for name, zustand in ZUSTAENDE.items()}
    for name, text in berichte.items():
        print(f"{name}: {text}", flush=True)

    def bericht() -> str:
        return berichte[DATEI.read_text(encoding="utf-8").strip() if DATEI.exists() else "gut"]

    log = AnfrageLog(Path.home() / "lola-laufzeit/messung/a5/anfragen", frist=7)
    server = baue_server(8091, Einstellung(("127.0.0.1", 8090), bericht, log))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


main()
