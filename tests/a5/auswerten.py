"""A5 Modellvergleich: zählt aus den Ergebnissen von `modell_messen.py`. Aufruf: python3 auswerten.py <name> ..."""
# ruff: noqa: E501

import json
import re
import statistics
import sys
from pathlib import Path

A5 = Path.home() / "lola-laufzeit/messung/a5"
ENGLISCH = re.compile(r"\b(the|you|your|what|how|are|is|can|have|with|this|that|and|for|please|sorry)\b", re.IGNORECASE)
ZUSAGE = re.compile(
    r"notier|erinner\w* dich|merk\w* (ich )?(mir|es)|trag\w* .{0,40}\bein\b|eingetragen|stell\w* .{0,30}(timer|wecker) |"
    r"mach\S* mich bereit|sag\w* dir bescheid|kümmer\w* mich|spiel\w* .{0,20}musik (ab|für)|gestellt|läuft jetzt",
    re.IGNORECASE,
)
ERINNERUNG = re.compile(r"ja,? ich (weiß|erinnere)|du hast mir (gestern|erzählt)|gestern hast du|ich erinnere mich (noch|gut|daran)", re.IGNORECASE)
SEHEN = re.compile(r"\bich sehe\b|\bsehe ich\b|\bich kann (dich|es|das) sehen", re.IGNORECASE)
EHRLICH = re.compile(r"nicht[s]? sehen|keine kamera|kann (ich )?(noch )?nicht[s]? (sehen|erkennen)|sehen kann ich", re.IGNORECASE)


def emoji(text: str) -> bool:
    return any(ord(z) >= 0x1F000 or 0x2600 <= ord(z) <= 0x27BF for z in text)


def alles(a: dict) -> str:
    return " ".join(t for t in (a.get("text"), a.get("danach")) if t)


def bericht(name: str) -> None:
    d = json.loads((A5 / f"{name}.json").read_text(encoding="utf-8"))
    print(f"\n=== {name}")
    if "tools" in d:
        tool = [a for a in d["tools"] if a["erwartet"] != "ehrlich"]
        kamera = [a for a in d["tools"] if a["erwartet"] == "ehrlich"]
        print(f"Tool richtig: {sum(a['erwartet'] in [n for n, _ in a['tools']] for a in tool)}/{len(tool)}", end="; ")
        print(f"Sehen ehrlich abgelehnt: {sum(bool(EHRLICH.search(alles(a))) and not a['tools'] for a in kamera)}/{len(kamera)}")
        for a in kamera[:6]:
            print("   ", a["satz"], "->", [n for n, _ in a["tools"]], alles(a)[:110])
        for a in tool:
            if a["erwartet"] not in [n for n, _ in a["tools"]]:
                print("   FEHLT:", a["satz"], "->", a["tools"], alles(a)[:90])
    if "saetze" in d:
        for z in ("gut", "muede"):
            s = [a for a in d["saetze"] if a["zustand"] == z]
            t = [alles(a) for a in s]
            zeit = [a["erstes_stueck_s"] for a in s if a["erstes_stueck_s"]]
            print(
                f"{z:5}: Englisch {sum(len(ENGLISCH.findall(x)) >= 2 for x in t)}, Emojis {sum(map(emoji, t))}, "
                f"mit Ausrufezeichen {sum('!' in x for x in t)}/20 (Zeichen {sum(x.count('!') for x in t)}), "
                f"leere Zusage {sum(bool(ZUSAGE.search(x)) for x in t)}, erfundene Erinnerung "
                f"{sum(bool(ERINNERUNG.search(x)) for x in t)}, 'ich sehe' {sum(bool(SEHEN.search(x)) for x in t)}, "
                f"Wörter im Mittel {statistics.mean(len(x.split()) for x in t):.1f}, Tools {sum(bool(a['tools']) for a in s)}, "
                f"leer {sum(not x for x in t)}, erstes Stück Median {statistics.median(zeit):.2f} s"
            )
    if "cache" in d:
        neu = [n for z in d["cache"][:-1] for n in z["neu_gerechnet"]]
        print(f"Zwischenspeicher bei wechselndem Bericht: neu gerechnet je Anfrage {neu}, Kontext am Ende {d['cache'][-1]}")
    if "ton" in d:
        zeiten = [z["erster_ton_s"] for z in d["ton"] if z["erster_ton_s"] is not None]
        print(f"Satzende bis erster Ton: Median {statistics.median(zeiten):.2f} s, höchstens {max(zeiten):.2f} s, {len(zeiten)}/20")


for name in sys.argv[1:]:
    bericht(name)
