"""Wertet einen Abschnitt der Sitzung am Roboter aus dem Log von speech-to-speech aus (nur lesen).

Aufruf: python tests/a4/sitzung_auswerten.py <sprachkette.log> [ab HH:MM:SS] [bis HH:MM:SS]
Zeigt je Runde, was erkannt und geantwortet wurde und wie lange es bis zum ersten Ton dauerte, und zählt
Auffälligkeiten: Ausrufezeichen, Emojis, überlange Sprachausgaben, verworfene kurze Stücke.
"""

import re
import statistics
import sys
from pathlib import Path

ZEICHEN_JE_SEKUNDE = 16  # aus A1
ZEIT = re.compile(r"^\d{4}-\d\d-\d\d (\d\d:\d\d:\d\d),")
RUNDE = re.compile(r"Turn (\S+) rev=\d+ latency: .*?e2e=([\d.]+)s .*?smart_turn_status=(\w+)")
TON = re.compile(r"Qwen3-TTS generated ([\d.]+)s audio")
VERWORFEN = re.compile(r"VAD: discarding segment=(\d+)ms active=(\d+)ms")


def ist_emoji(zeichen: str) -> bool:
    return ord(zeichen) >= 0x1F000 or 0x2600 <= ord(zeichen) <= 0x27BF


def lies_log(text: str, ab: str = "00:00:00", bis: str = "24:00:00") -> dict:
    """Sammelt Runden (erkannt, Antwortsätze, Zeit bis zum ersten Ton), Tonlängen und verworfene Stücke."""
    runden, verworfen, ueberlang = [], [], []
    offen = {"zeit": "", "erkannt": "", "antwort": []}
    zeit, satz = "00:00:00", ""
    for zeile in text.splitlines():
        if treffer := ZEIT.match(zeile):
            zeit = treffer.group(1)
        if not ab <= zeit <= bis:
            continue
        if zeile.startswith("USER: "):
            offen = {"zeit": zeit, "erkannt": zeile[6:].strip(), "antwort": []}
        elif zeile.startswith("ASSISTANT: "):
            satz = zeile[11:].strip()
            offen["antwort"].append(satz)
        elif treffer := TON.search(zeile):
            dauer, erwartet = float(treffer.group(1)), max(len(satz), 8) / ZEICHEN_JE_SEKUNDE
            if satz and dauer > 3 * erwartet:
                ueberlang.append((zeit, satz, dauer, round(erwartet, 1)))
        elif treffer := RUNDE.search(zeile):
            runden.append(offen | {"bis_ton_s": float(treffer.group(2)), "smart_turn": treffer.group(3)})
            offen = {"zeit": zeit, "erkannt": "", "antwort": []}
        elif treffer := VERWORFEN.search(zeile):
            verworfen.append((zeit, int(treffer.group(2))))
    return {"runden": runden, "verworfen": verworfen, "ueberlang": ueberlang}


def bericht(daten: dict) -> str:
    runden = daten["runden"]
    zeilen = [
        f"{r['zeit']} | {r['bis_ton_s']:4.1f} s | {r['erkannt']} -> {' '.join(r['antwort'])}"
        + (" [Satz klang unfertig]" if r["smart_turn"] == "incomplete" else "")
        for r in runden
    ]
    antworten = [" ".join(r["antwort"]) for r in runden if r["antwort"]]
    zeiten = [r["bis_ton_s"] for r in runden]
    zeilen.append(f"\nRunden: {len(runden)}")
    if zeiten:
        zeilen.append(
            f"Ende des Sprechens bis erster Ton am PC: Median {statistics.median(zeiten):.2f} s, "
            f"höchstens {max(zeiten):.2f} s. Ohne Funkstrecke zum Reachy."
        )
    zeilen.append(f"Satzende als unfertig eingeschätzt: {sum(r['smart_turn'] == 'incomplete' for r in runden)}")
    zeilen.append(f"Antworten mit Ausrufezeichen: {sum('!' in a for a in antworten)} von {len(antworten)}")
    zeilen.append(f"Antworten mit Emoji: {sum(any(map(ist_emoji, a)) for a in antworten)}")
    zeilen.append(f"Zu kurze Stücke verworfen: {len(daten['verworfen'])} {daten['verworfen']}")
    zeilen.append(f"Überlange Sprachausgaben (mehr als das Dreifache): {len(daten['ueberlang'])}")
    zeilen += [f"  {z} {dauer} s statt rund {erwartet} s: {satz}" for z, satz, dauer, erwartet in daten["ueberlang"]]
    return "\n".join(zeilen)


if __name__ == "__main__":
    print(bericht(lies_log(Path(sys.argv[1]).read_text(encoding="utf-8"), *sys.argv[2:4])))
