# Pausenerkennung vormessen, ohne Roboter (9. Oktober 2026)

Nur Branch `test/b4`, wird nie gemergt. Rohdaten lokal in `~/lola-laufzeit/messung/pause/`.
Vorab-Ja von Patrick: keine neue Abhängigkeit, nur Einstellungen von speech-to-speech, kein Code dort.
Die endgültige Einstellung entscheidet Patrick am Roboter.

## Plan in drei Sätzen (vor Beginn geschrieben)
1. **Was ich tue:** Ich starte die Kette ohne App (`lola_start kette`) und tausche je Stufe nur die
   Sprachkette gegen eine mit anderen Schaltern aus; ein Messprogramm spielt wie in B4 die App und spielt
   die 20 Aufnahmen aus A1 und künstliche Aufnahmen mit Denkpause (0,3 / 0,5 / 0,7 s) ein.
2. **Welche Dateien:** auf `test/b4` vier Skripte unter `tests/b4/` (Aufnahmen bauen, Stufen fahren, messen,
   auswerten) und dieses Protokoll; auf `entwicklung` nur MESSUNGEN, ENTSCHEIDUNGEN, BACKLOG, FAHRPLAN, CHANGELOG.
3. **Wie viel:** rund 250 Zeilen Messskripte, kein Produktcode; der Reachy wird nicht angefasst
   (keine App, `lola_start stop` legt ihn nur schlafen, wenn die App lief).

Grafikspeicher vor dem Start: 635 MiB belegt. Die Kette braucht nach B4 rund 9,3 GB von 12 GB.

## Was der Code von speech-to-speech sagt (gelesen, Stand `8024ccf`)
Die Pausenerkennung hat zwei Stufen, nicht eine Stille-Schwelle:
1. **Silero** erkennt Sprache (`--thresh` 0,6). Nach 64 ms Stille (`--min_silence_ms`) gilt das Stück als
   beendet. Ein Stück mit weniger als 384 ms Sprache (`--min_speech_ms`) wird verworfen.
2. **Smart Turn** (zweites kleines Modell) schätzt, ob der Satz fertig klingt.
   Fertig: Erkennung und Sprachmodell laufen sofort los, die Antwort wird aber 800 ms zurückgehalten
   (`--speculative_reopen_ms`); spricht der Mensch in dieser Zeit weiter, gilt alles als ein Satz.
   Nicht fertig: 600 ms warten (`--smart_turn_incomplete_delay_ms`), Antwort frühestens nach 2 s
   (`--smart_turn_max_wait_ms`).

„Stille-Schwelle senken“ heißt hier also: die Rückhaltezeit von 800 ms senken.
„Mindestlänge“ ist `--min_speech_ms`.

## Stufen
| Name | Schalter |
| --- | --- |
| standard | keine |
| halt600 / halt400 / halt200 | `--speculative_reopen_ms` 600 / 400 / 200 |
| ohne-smart | `--no_smart_turn` |
| kurz256 / kurz192 / kurz128 | `--min_speech_ms` 256 / 192 / 128 |
| schwelle04 | `--thresh 0.4` |

Je Stufe: die 20 Aufnahmen aus A1 (Zeit bis zum ersten Ton, Antwort auf „Ja.“) und 8 Sätze mal 3 Pausen.
„Zu früh abgeschnitten“ heißt: Der erste Ton einer Antwort kommt, bevor die Aufnahme zu Ende ist, oder der
zuletzt erkannte Text enthält den zweiten Satzteil nicht.

## Ablauf und Ergebnis (13:34 bis 14:40 Uhr)
- `lola_start kette`, Grafikspeicher danach: llama-server 6.012 MiB, speech-to-speech 2.608 MiB.
  Der Reachy blieb im Schlaf (Motoren aus, am Ende geprüft). Am Ende `lola_start stop`, 635 MiB belegt.
- `pause_aufnahmen.py`: 8 Sätze mal 3 Pausen. Bei Satz 8 und 9 ist die leiseste Stelle nicht still
  (Pegel rund ein Zehntel des Mittels), dort kann der Schnitt hörbar sein.
- `pause_stufen.py` tauscht je Stufe nur die Sprachkette aus, `pause_reihe.py` misst, `pause_auswerten.py`
  baut die Tabellen. Nachträglich ergänzte Stufen: `naht300`, `stille200` (wegen „Stopp!“), `halt1200`
  (weil 0,7 s Pause bei 800 ms abschnitt), `standard2` (Streuung), `kurz256` als voller Lauf.
- Ergebnis und Tabellen stehen auf `entwicklung` in `MESSUNGEN.md`, die Empfehlung in `ENTSCHEIDUNGEN.md`.
- Die Stufen `schwelle03-kurz256`, `kurz256-halt600`, `kurz256-halt400` sind vorbereitet, aber nicht gefahren.

## Was ich falsch angenommen hatte
- „Stille-Schwelle senken macht schneller“: stimmt hier nicht. Die Antwort wartet bei normalen Sätzen gar
  nicht auf die Rückhaltezeit (im Log `hold=0.00s`), weil Erkennung plus Sprachmodell länger brauchen.
- „Stopp!“ wird von der Pausenerkennung zerlegt: nicht belegt. Die Aufnahme selbst wird schlecht erkannt (A1).
- Zwei Warteschleifen von mir erkannten sich selbst als laufende Messung; von Hand beendet, kein Schaden.

## Nicht geprüft
Echte Stimmen, Raumgeräusche (springt 256 ms auf Geräusche an?), echtes „ähm“, die Funkstrecke zum Reachy.
