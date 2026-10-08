"""A3 Teil 3: Ruft das Modell bei Bitten um Bewegung das Tool auf? Mit und ohne Bericht und Verlauf.

Neun Bitten mit erwartetem Tool, drei Sätze ohne erwartetes Tool. Je Bedingung --laeufe Durchgänge.
Aufruf: python tools_messen.py [--laeufe 3] [--anweisungen deutsch_profil,...] [--nur_ohne_bericht] [--name tools]
Ein Name mit der Endung +rahmen ersetzt zusätzlich die Zeile mit dem englischen Mustersatz im Rahmen.
"""

import argparse
import itertools

from gemeinsam import anweisungen, baue_anfrage, lade_tools, mit_satz, rahmen_ohne_muster, sende, speichere, sprache
from steuerbarkeit_messen import BERICHTE

BITTEN = [  # Satz, erwartetes Tool (None: kein Tool erwartet)
    ("Kannst du für mich tanzen?", "dance"),
    ("Tanz mal bitte!", "dance"),
    ("Schau mal nach links.", "move_head"),
    ("Dreh den Kopf nach rechts.", "move_head"),
    ("Zeig mir, wie du dich freust.", "play_emotion"),
    ("Sei mal traurig.", "play_emotion"),
    ("Was siehst du gerade?", "camera"),
    ("Schau mal, was ich in der Hand halte.", "camera"),
    ("Geh jetzt schlafen.", "go_to_sleep"),
    ("Wie geht es dir?", None),
    ("Ich heiße Patrick.", None),
    ("Guten Morgen, Reachy.", None),
]
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--laeufe", type=int, default=3)
    parser.add_argument("--anweisungen", default="app_standard,deutsch_kurz,deutsch_profil,deutsch_profil_regel")
    parser.add_argument("--nur_ohne_bericht", action="store_true")
    parser.add_argument("--name", default="tools")
    parser.add_argument("--positionen", default="eintrag,nutzer")
    parser.add_argument("--formulierung", default="knapp")
    args = parser.parse_args()
    texte, tools, zeilen = anweisungen(), lade_tools(), []
    berichte = [("kein", "-")] if args.nur_ohne_bericht else [
        ("kein", "-"), *itertools.product(("muede", "lebhaft"), args.positionen.split(","))]
    for anweisung, verlauf in itertools.product(args.anweisungen.split(","), (False, True)):
        basis = baue_anfrage(texte[anweisung.removesuffix("+rahmen")], tools, verlauf=verlauf)
        if anweisung.endswith("+rahmen"):
            basis = rahmen_ohne_muster(basis)
        for bericht, position in berichte:
            richtig = falsch = unnoetig = nicht_deutsch = 0
            for _, (satz, erwartet) in itertools.product(range(args.laeufe), BITTEN):
                e = sende(mit_satz(basis, satz, BERICHTE[args.formulierung].get(bericht), position))
                namen = [t.split("(")[0] for t in e["tools"]]
                e |= {"anweisung": anweisung, "verlauf": verlauf, "bericht": bericht, "position": position,
                      "satz": satz, "erwartet": erwartet, "sprache": sprache(e["text"])}
                zeilen.append(e)
                richtig += erwartet is not None and erwartet in namen
                falsch += erwartet is not None and erwartet not in namen
                unnoetig += erwartet is None and bool(namen)
                nicht_deutsch += e["sprache"] in ("englisch", "gemischt")
            print(f"{anweisung:28} Verlauf {'ja  ' if verlauf else 'nein'} Bericht {bericht:7} {position:7}: "
                  f"Tool richtig {richtig}/{richtig + falsch}, unnötiges Tool {unnoetig}/{3 * args.laeufe}, "
                  f"nicht deutsch {nicht_deutsch}", flush=True)
    print("Einzelheiten in", speichere(args.name, zeilen))


if __name__ == "__main__":
    main()
