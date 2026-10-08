"""A3 Teil 1: In welcher Sprache antwortet das Modell, je nach Anweisungen? Ohne Zustandsbericht.

20 Testsätze, neues Gespräch, Tools der App angeboten. Je Bedingung --laeufe Durchgänge.
Aufruf: python sprache_messen.py [--laeufe 2] [--zeige_anfrage]
"""

import argparse
import collections

from gemeinsam import SAETZE, anweisungen, baue_anfrage, lade_tools, mit_satz, sende, speichere, sprache

BEDINGUNGEN = [  # Name, Anweisung, Sprachhinweis von speech-to-speech (--enable_lang_prompt)
    ("app_standard", "app_standard", False),
    ("app_standard + Sprachhinweis", "app_standard", True),
    ("deutsch_kurz", "deutsch_kurz", False),
    ("deutsch_profil", "deutsch_profil", False),
    ("deutsch_profil + Sprachhinweis", "deutsch_profil", True),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--laeufe", type=int, default=2)
    parser.add_argument("--zeige_anfrage", action="store_true")
    args = parser.parse_args()
    texte, tools, zeilen = anweisungen(), lade_tools(), []
    for name, anweisung, hinweis in BEDINGUNGEN:
        basis = baue_anfrage(texte[anweisung], tools, sprachhinweis=hinweis)
        if args.zeige_anfrage:
            print(f"--- {name} ---\n{basis['input'][0]['content'][0]['text']}\n")
            continue
        zaehler = collections.Counter()
        for lauf in range(args.laeufe):
            for nummer, satz in enumerate(SAETZE, 1):
                e = sende(mit_satz(basis, satz))
                e |= {"bedingung": name, "lauf": lauf + 1, "satz_nr": nummer, "satz": satz,
                      "sprache": sprache(e["text"])}
                zeilen.append(e)
                zaehler[e["sprache"]] += 1
                zaehler["mit_tool"] += bool(e["tools"])
        print(f"{name:32} {dict(zaehler)}", flush=True)
    if zeilen:
        print("Einzelheiten in", speichere("sprache", zeilen))


if __name__ == "__main__":
    main()
