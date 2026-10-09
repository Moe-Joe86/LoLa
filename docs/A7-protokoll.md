# A7 – Machbarkeitstest Sinne (9. Oktober 2026)

Nur Branch `test/a7`, wird nie gemergt. Rohdaten lokal in `~/lola-laufzeit/messung/a7/`
(Tonaufnahme und Kamerabild aus der Wohnung: nie ins Repo, nie ins Netz).

## Plan in drei Sätzen (vor Beginn geschrieben)
1. **Was ich tue:** Ich starte LoLa mit `lola_start` und lasse ein zweites Programm auf dem PC denselben
   Ton- und Bildstrom des Reachy per WebRTC mitlesen, erst 60 s ohne, dann 90 s mit dem Mitleser, jeweils
   mit denselben eingeschleusten Sätzen (`conversation.say`).
2. **Welche Dateien:** `tests/a7/mitlesen.py` (zweites Programm, nutzt die Reachy-Bibliothek aus
   `~/lola-laufzeit/app-venv`, keine neue Abhängigkeit), `tests/a7/auswerten.py` und dieses Protokoll;
   auf `entwicklung` nur das Ergebnis in ENTSCHEIDUNGEN, MESSUNGEN und die FAHRPLAN-Zeile.
3. **Wie viel und was am Reachy:** rund 200 Zeilen; der Reachy wird nur geweckt (durch die App) und am Ende
   mit `lola_start stop` schlafen gelegt, gespeichert oder installiert wird dort nichts.

Gemessen wird: Bildrate, Auflösung und Schärfe; Abtastrate, Pegel und Lücken im Ton; Verzögerung
(Kopfbewegung im Log der App bis zur Bildänderung; Sprechbeginn bis zum Pegelanstieg); CPU-Last von App,
Sprachkette und Mitleser; Fehlerzeilen in App, Sprachkette und Daemon; Regeltakt des Daemons.
Nicht messbar ohne Patrick: ob LoLa hörbar weiterspricht und wie Sprache einer Person klingt.

## Ablauf (09:25 bis 09:34 Uhr)
- Mitleser: `GstWebRTCClient` aus der Reachy-Bibliothek, direkt, ohne Steuerverbindung zum Daemon.
- Phase A (ohne Mitleser, 3 Sätze, 9 s Abstand), Phase B (mit, dieselben Sätze), Phase C (ohne, 4 Sätze mit
  20 s Abstand), Phase D (mit, dieselben). Sätze eingeschleust über `conversation.say`.

## Gemessen
| Größe | ohne Mitleser | mit Mitleser |
| --- | --- | --- |
| CPU App (Prozent eines Kerns von 16) | 51 | 48 bis 54 |
| CPU speech-to-speech | 10 | 9 |
| CPU Mitleser | - | 52 |
| Regeltakt des Daemons, Mittel | 48,9 bis 49,4 Hz | 45,7 bis 46,7 Hz |
| längster Abstand im Regeltakt | 21 bis 24 ms | 35 bis 39 ms |
| Fehler im Regelkreis | 0 | 0 |
| eingeschleuste Sätze ausgeführt | 6 von 7 | 6 von 7 |

- **Bild beim Mitleser:** 1280×720, 28,8 und 29,3 Bilder je Sekunde, Abstand im Mittel 35 ms, 99 % unter
  143 ms, längste Lücke 452 ms; 11 und 9 Lücken über 200 ms in 75 und 100 s. Angesehen: brauchbar, aber
  sichtbar zusammengedrückt (Klötzchen, verwaschene Flächen in der Ferne).
- **Ton beim Mitleser:** 16 kHz, 2 Kanäle; es kamen 15.549 und 15.344 Werte je Sekunde an (3 bis 4 % unter
  dem Soll), je Lauf 4 Lücken über 100 ms, längste 210 ms. Ob die App dieselben Lücken hat: nicht gemessen.
- **Verzögerung Bild:** vom Log-Eintrag „Tool call: move_head“ bis zur sichtbaren Bildänderung 0,44 bis
  0,77 s (5 Werte). Darin steckt auch der Anlauf der Motoren.
- **Verzögerung Ton:** nicht messbar ohne eine Schallquelle im Raum.
- **Grafikspeicher:** unverändert rund 9,55 GB, der Mitleser nutzt keinen.

## Nebenbefund (gehört zu A6, hier nur festgehalten)
Zweimal ging ein eingeschleuster Satz verloren, einmal mit und einmal ohne Mitleser: speech-to-speech meldet
`JSONDecodeError: Expecting value` beim Empfang, beendet die Sitzung, die App verbindet sich nach 1,4 s neu.
Der Satz wird nicht ausgeführt. Ursache offen; der Mitleser ist es nicht.

## Nicht geprüft
Ob LoLa hörbar weiterspricht, während der Mitleser verbunden ist (er sendet wie jeder Client einen stillen
Tonstrom zum Reachy); Sprache einer Person; mehr als 100 s am Stück; zwei Mitleser.
