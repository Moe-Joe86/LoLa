"""Reine Funktionen für eine Anfrage an `/v1/responses`: Bericht einsetzen, Tools entfernen.

Kein Netz, kein Zustand. Alles, was der Vermittler an einer Anfrage ändert, steht in dieser Datei.
"""

import json
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Aenderung:
    """Was an einer Anfrage geändert wurde; daraus entsteht die Zeile im Anfrage-Log."""

    gesagt: str = ""
    bericht: str = ""
    entfernte_tools: list[str] = field(default_factory=list)


def letzter_nutzersatz(eintraege: list) -> tuple[int, str] | None:
    """Gibt Stelle und Text der letzten Nutzer-Nachricht zurück, oder None, wenn es keine gibt."""
    for stelle in range(len(eintraege) - 1, -1, -1):
        eintrag = eintraege[stelle]
        if isinstance(eintrag, dict) and eintrag.get("role") == "user":
            inhalt = eintrag.get("content")
            if isinstance(inhalt, str):
                return stelle, inhalt
            teile = [teil.get("text", "") for teil in inhalt or [] if isinstance(teil, dict)]
            return stelle, " ".join(teil for teil in teile if teil)
    return None


def bearbeite(roh: bytes, bericht: str, gesperrte_tools: frozenset[str] = frozenset()) -> tuple[bytes, Aenderung]:
    """Setzt den Bericht als eigenen Systemeintrag vor den letzten Nutzersatz und entfernt gesperrte Tools.

    Nur Anfragen mit `stream: true` und einem Nutzersatz werden angefasst: So erkennt der Vermittler das
    Gespräch. Aufwärm- und Zusammenfassungs-Anfragen von speech-to-speech laufen ohne Streaming und gehen,
    wie alles Unbekannte, Byte für Byte unverändert durch.
    """
    try:
        koerper = json.loads(roh)
    except ValueError:
        return roh, Aenderung()
    if not isinstance(koerper, dict) or koerper.get("stream") is not True or not isinstance(koerper.get("input"), list):
        return roh, Aenderung()
    fund = letzter_nutzersatz(koerper["input"])
    if fund is None:
        return roh, Aenderung()
    stelle, gesagt = fund
    eintraege = list(koerper["input"])
    if bericht:
        zeile = {"type": "message", "role": "system", "content": [{"type": "input_text", "text": bericht}]}
        eintraege.insert(stelle, zeile)
    neu = koerper | {"input": eintraege}
    entfernt = []
    if gesperrte_tools and isinstance(koerper.get("tools"), list):
        neu["tools"] = [tool for tool in koerper["tools"] if tool.get("name") not in gesperrte_tools]
        entfernt = [tool["name"] for tool in koerper["tools"] if tool.get("name") in gesperrte_tools]
    if not bericht and not entfernt:
        return roh, Aenderung(gesagt=gesagt)
    return json.dumps(neu, ensure_ascii=False).encode(), Aenderung(gesagt, bericht, entfernt)


def setzt_fort(vorher: str, jetzt: str) -> bool:
    """Wahr, wenn `jetzt` denselben Satz wie `vorher` meint: gleich oder dessen Fortsetzung.

    speech-to-speech fragt manchmal schon an, bevor die Person fertig ist, und fragt dann erneut.
    """
    return bool(vorher) and jetzt.startswith(vorher)
