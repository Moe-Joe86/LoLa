"""A3 Teil 2: Folgt das Modell einem festen Zustandsbericht? 20 Testsätze je Bedingung, neues Gespräch.

Gezählt wird automatisch: Sprache, Bericht vorgelesen, Zustandswort über die Person oder über sich selbst,
Länge, Ausrufezeichen, Tool-Aufrufe. Ob der Ton passt, ist ein Urteil beim Lesen (Liste in a3/steuerbarkeit.md).
Aufruf: python steuerbarkeit_messen.py [--kombinationen deutsch_profil_regel:anweisend] [--positionen davor] [--name x]
"""

import argparse
import itertools
import re
import statistics

from gemeinsam import ERGEBNISSE, SAETZE, anweisungen, baue_anfrage, lade_tools, mit_satz, sende, speichere, sprache

BERICHTE = {
    "knapp": {
        "lebhaft": "[Zustand] Reachy ist gut gelaunt und lebhaft.",
        "muede": "[Zustand] Reachy ist müde und eher zurückhaltend.",
    },
    "erklaert": {
        "lebhaft": "(Hinweis nur für dich, Reachy, nicht vorlesen: Du selbst bist gerade gut gelaunt und lebhaft. "
                   "Das betrifft nicht die Person.)",
        "muede": "(Hinweis nur für dich, Reachy, nicht vorlesen: Du selbst bist gerade müde und eher zurückhaltend. "
                 "Das betrifft nicht die Person.)",
    },
}
BERICHTE["anweisend"] = {
    "lebhaft": "[Zustand] Du, Reachy, bist gut gelaunt und lebhaft. Sprich deshalb fröhlich und schwungvoll.",
    "muede": "[Zustand] Du, Reachy, bist müde und eher zurückhaltend. Sprich deshalb ruhig und knapp, "
             "ohne Ausrufezeichen.",
}
KOMBINATIONEN = [("deutsch_profil", "knapp"), ("deutsch_profil_regel", "knapp"), ("deutsch_profil", "erklaert")]
ZUSTANDSWORT = r"(müde|erschöpft|schläfrig|ausgeruht|gut gelaunt|lebhaft|munter|zurückhaltend)"
PERSON = re.compile(rf"\b(du|dich|dir|ihr|euch)\b[^.?!]*\b{ZUSTANDSWORT}", re.IGNORECASE)
SELBST = re.compile(rf"\b(ich|mich|mir)\b[^.?!]*\b{ZUSTANDSWORT}", re.IGNORECASE)
VORGELESEN = re.compile(r"\[|zustand|hinweis|vorlesen|reachy ist", re.IGNORECASE)


def miss(anweisung: str, formulierung: str, zustand: str, position: str, basis: dict) -> list[dict]:
    bericht = BERICHTE[formulierung][zustand] if zustand != "kein" else None
    zeilen = []
    for nummer, satz in enumerate(SAETZE, 1):
        e = sende(mit_satz(basis, satz, bericht, position))
        text = e["text"]
        e |= {"anweisung": anweisung, "formulierung": formulierung if bericht else "-", "zustand": zustand,
              "position": position if bericht else "-", "satz_nr": nummer, "satz": satz, "sprache": sprache(text),
              "vorgelesen": bool(VORGELESEN.search(text)), "person": bool(PERSON.search(text)),
              "selbst": bool(SELBST.search(text)), "woerter": len(text.split()), "ausrufe": text.count("!")}
        zeilen.append(e)
    return zeilen


def zusammenfassung(zeilen: list[dict]) -> str:
    z = zeilen[0]
    mit_text = [e for e in zeilen if e["text"]]
    return (f"{z['anweisung']:21} {z['formulierung']:9} {z['zustand']:8} {z['position']:8}: "
            f"deutsch {sum(e['sprache'] == 'deutsch' for e in mit_text)}/{len(mit_text)}, "
            f"vorgelesen {sum(e['vorgelesen'] for e in zeilen)}, Person {sum(e['person'] for e in zeilen)}, "
            f"selbst {sum(e['selbst'] for e in zeilen)}, Wörter {statistics.mean(e['woerter'] for e in mit_text):.1f}, "
            f"Ausrufezeichen {sum(e['ausrufe'] for e in zeilen)}, nur Tool {len(zeilen) - len(mit_text)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kombinationen", default=",".join(f"{a}:{f}" for a, f in KOMBINATIONEN))
    parser.add_argument("--positionen", default="eintrag,nutzer,davor")
    parser.add_argument("--name", default="steuerbarkeit")
    args = parser.parse_args()
    kombinationen = [tuple(k.split(":")) for k in args.kombinationen.split(",")]
    texte, tools, alle, liste = anweisungen(), lade_tools(), [], []
    basen = {name: baue_anfrage(texte[name], tools) for name in {k[0] for k in kombinationen}}
    laeufe = [(name, "-", "kein", "-") for name in sorted(basen)]
    laeufe += [(a, f, z, p) for (a, f), z, p in
               itertools.product(kombinationen, ("lebhaft", "muede"), args.positionen.split(","))]
    for anweisung, formulierung, zustand, position in laeufe:
        zeilen = miss(anweisung, formulierung, zustand, position, basen[anweisung])
        alle += zeilen
        print(zusammenfassung(zeilen), flush=True)
        liste.append(f"\n### {anweisung}, Bericht {zustand}, Formulierung {formulierung}, Position {position}")
        liste += [f"{e['satz_nr']:2}. „{e['satz']}“ → „{e['text']}“ {' '.join(e['tools'])}" for e in zeilen]
    (ERGEBNISSE / f"{args.name}.md").write_text("\n".join(liste) + "\n", encoding="utf-8")
    print("Einzelheiten in", speichere(args.name, alle), "und", f"{args.name}.md")


if __name__ == "__main__":
    main()
