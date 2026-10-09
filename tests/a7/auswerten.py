"""Wertet einen Lauf von mitlesen.py aus. Aufruf: python tests/a7/auswerten.py <mitlesen.jsonl> <app.log>"""

import datetime as dt
import json
import re
import sys

import numpy as np


def zeit(text: str, tag: str) -> float:
    return dt.datetime.strptime(f"{tag} {text}", "%Y-%m-%d %H:%M:%S,%f").timestamp()


def main(messdatei: str, app_log: str) -> None:
    zeilen = [json.loads(zeile) for zeile in open(messdatei, encoding="utf-8")]
    bilder = [z for z in zeilen if z["art"] == "bild"]
    ton = [z for z in zeilen if z["art"] == "ton"]
    abstand = np.diff([z["t"] for z in bilder]) * 1000
    print(
        f"Bild: {bilder[0]['form'][1]}x{bilder[0]['form'][0]}, "
        f"{len(bilder) / (bilder[-1]['t'] - bilder[0]['t']):.1f} je s, "
        f"Abstand Mittel {abstand.mean():.0f} ms, 99 % {np.percentile(abstand, 99):.0f} ms, "
        f"höchstens {abstand.max():.0f} ms, "
        f"Lücken über 200 ms: {(abstand > 200).sum()}, Schärfe {[z['schaerfe'] for z in bilder if 'schaerfe' in z]}"
    )
    dauer = ton[-1]["t"] - ton[0]["t"]
    luecken = np.diff([z["t"] for z in ton]) * 1000
    pegel = np.array([z["pegel"] for z in ton])
    print(
        f"Ton: {sum(z['werte'] for z in ton) / dauer:.0f} Werte je s (Soll 16000), "
        f"Abstand höchstens {luecken.max():.0f} ms, "
        f"Lücken über 100 ms: {(luecken > 100).sum()}, Pegel Median {np.median(pegel):.4f}, höchstens {pegel.max():.4f}"
    )
    tag = dt.datetime.fromtimestamp(zeilen[0]["t"]).strftime("%Y-%m-%d")
    ruhe_bild = np.median([z["aenderung"] for z in bilder])
    for zeile in open(app_log, encoding="utf-8"):
        treffer = re.match(r"\d{4}-\d\d-\d\d (\d\d:\d\d:\d\d,\d+) .*tools\.move_head:\d+ \| Tool call: (.*)", zeile)
        if not treffer or not zeilen[0]["t"] <= (beginn := zeit(treffer.group(1), tag)) <= zeilen[-1]["t"] - 3:
            continue
        erst = next(
            (z["t"] - beginn for z in bilder if z["t"] >= beginn and z["aenderung"] > max(3 * ruhe_bild, 1.0)), None
        )
        print(
            f"{treffer.group(1)} {treffer.group(2)}: Bild ändert sich nach {erst:.2f} s"
            if erst
            else f"{treffer.group(1)}: keine Änderung"
        )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
