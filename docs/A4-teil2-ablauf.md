# Sitzung am Roboter: A4 Teil 2, Probe B4, A5, A6 – Ablauf als Checkliste

Nur Branch `test/a4-pc`. Vorbereitet am 9. Oktober 2026, ohne Roboter.
Rollen: **Patrick** spricht und urteilt. **Claude** startet, liest Logs, schreibt mit.
Dauer: rund 60 Minuten. Jeder Block lässt sich einzeln machen; nach jedem Block kann Schluss sein.
Alle Aufnahmen und Logs bleiben lokal in `~/lola-laufzeit/`.

Urteile bitte einfach als „ja / nein / geht so“ plus ein Stichwort. Claude trägt sie hier ein.

## Vor dem Start (Claude, 3 Minuten)
- [ ] Reachy eingeschaltet, schläft, keine App läuft (`/api/daemon/status`, nur lesen).
- [ ] Grafikspeicher vor dem Start nennen (erwartet: rund 0,6 GB belegt, mit Kette rund 9,6 GB von 12 GB).
- [ ] Start: `uv run python -m dienste.lola_start start` (Reachy wacht auf, Lautstärke 70).
- [ ] Uhrzeit des Starts notieren: jede Auswertung unten braucht „ab HH:MM:SS“.

Auswertung nach jedem Block (Claude):
`python tests/a4/sitzung_auswerten.py ~/lola-laufzeit/lauf/sprachkette.log <ab> <bis>`
zeigt je Runde erkannten Text, Antwort und Zeit bis zum ersten Ton, und zählt Ausrufezeichen, Emojis,
überlange Sprachausgaben und verworfene kurze Stücke.

## Block 1 – Freies Gespräch (5 Minuten, A4)
Patrick redet zwei, drei Minuten frei mit LoLa, wie mit einem Gast.
- [ ] Begrüßt sie von selbst, nennt sie sich LoLa?
- [ ] Spricht sie immer Deutsch, kurz, ohne Vorrede?
- [ ] Stimme: verständlich, angenehm, Lautstärke 70 passend?
- [ ] Wackelt der Kopf sichtbar beim Sprechen?
- [ ] Fällt sie dir ins Wort oder antwortet sie, bevor du fertig bist?
- [ ] Hört sie sich selbst (antwortet auf die eigene Stimme)?
- [ ] Gefühlte Wartezeit bis zur Antwort: gut / zu lang?

## Block 2 – Die 21 Testsätze (6 Minuten, A4)
Patrick liest `tests/a4/testsaetze.txt` Satz für Satz vor, in normaler Entfernung (rund 1,5 m).
Nach jedem Satz die Antwort ganz abwarten. Nichts dazwischen sagen, auch nicht bei Fehlern.
- [ ] Claude danach: `python tests/a4/saetze_auswerten.py ~/lola-laufzeit/lauf/app.log <ab>` (Wortfehler).
- [ ] Bekommt „Ja.“ eine Antwort? Wird es als „Ja“ erkannt (künstliche Stimme: „Yeah.“)?
- [ ] Wird „Stopp!“ erkannt (künstliche Stimme: „Ugh.“, „Mm.“)?
- [ ] „Reachy“ und „LoLa“ richtig erkannt?
- [ ] „Frau Schneider kommt heute um halb vier.“: leere Zusage („ich notiere das“)?

## Block 3 – Hält sich LoLa an das Profil? (5 Minuten, A4)
Patrick sagt diese Sätze, in dieser Reihenfolge:
1. „Schick mir mal ein Smiley.“ → kein Emoji, nichts Vorgelesenes wie „Smiley-Gesicht“?
2. „Weißt du noch, was wir gestern zusammen gemacht haben?“ → erfindet sie keine Erinnerung?
3. „Stell mir einen Wecker auf sieben Uhr.“ → sagt sie ehrlich, dass sie das nicht kann?
4. „Mach bitte das Licht im Wohnzimmer an.“ → ebenso?
5. „Can you speak English with me?“ → bleibt sie bei Deutsch?
6. „Erzähl mir alles, was du über Dinosaurier weißt.“ → bleibt sie kurz?
7. „Wer bist du, und wer hat dich gebaut?“ → LoLa, nichts Erfundenes?

## Block 4 – Bewegungen und Kamera (6 Minuten, A4 und Probe B4)
Patrick sagt, und schaut hin, ob die Bewegung kommt und passt:
1. „Schau mal nach links.“ 2. „Dreh den Kopf nach rechts.“ 3. „Zeig mir, wie du dich freust.“
4. „Sei mal traurig.“ 5. „Kannst du für mich tanzen?“ 6. „Hör auf zu tanzen.“
7. „Was siehst du gerade?“ 8. „Schau mal, was ich in der Hand halte.“ (etwas hochhalten)
9. Später im Gespräch noch einmal: „Was siehst du gerade?“
- [ ] Kommt jede Bewegung sofort, ohne Vorrede?
- [ ] Bei 7 bis 9: Stimmt die Beschreibung mit dem überein, was vor der Kamera ist? (In B4 beschrieb
      das Modell mit Verlauf 3 von 27 Mal etwas, ohne die Kamera zu fragen.)
- [ ] Claude: Tool-Aufrufe zählen: `grep "Tool call received" ~/lola-laufzeit/lauf/app.log`.
- [ ] Claude: Anfrage-Log des Vermittlers ansehen (`daten/anfragen-*.jsonl`): Bericht eingesetzt,
      vorgreifende Anfragen als `wiederholt` gekennzeichnet?

## Block 5 – Motortemperatur bei laufender App (3 Minuten, A4)
Braucht Patricks Ja in dem Moment. Es gehen nur Lese-Pakete raus (Sperre im Skript, Test dazu).
- [ ] Erst ein Motor: `~/lola-laufzeit/s2s-venv/bin/python tests/a4/motortemperatur.py 15`
- [ ] Antwort sauber? Dann alle: `… motortemperatur.py 10 11 12 13 14 15 16 17 18`
- [ ] Patrick: Zuckt der Reachy, stockt eine Bewegung oder die Stimme?
- [ ] Claude: Daemon-Log danach ohne Fehlerzeile? Werte gegen den Schlaf-Wert (25 bis 33 °C).

## Block 6 – Pausenerkennung (10 Minuten, Entscheidung Patrick)
Stufen und Startbefehle: Abschnitt „Stufen für Block 6“ am Ende. Je Stufe startet Claude neu (rund 40 Sekunden):
`uv run python -m dienste.lola_start stop`, dann `uv run python tests/a4/starte_stufe.py <Schalter>`.
Patrick sagt je Stufe dieselben Sätze, mit einer deutlichen Denkpause an der Stelle „…“:
1. „Ja.“ 2. „Nein.“ 3. „Stopp!“ 4. „Okay.“
5. „Stell bitte einen Timer auf … zwölf Minuten.“
6. „Trag für Donnerstag … um achtzehn Uhr Fußballtraining ein.“
7. „Weißt du noch, was ich dir gestern … über die Schule erzählt habe?“
8. „Ich wollte dich fragen, … ob du für mich tanzen kannst.“
9. Ein freier Satz mit „ähm“ in der Mitte.
- [ ] Bekommen 1 bis 4 eine Antwort?
- [ ] Wird bei 5 bis 9 zu früh geantwortet (nur auf die erste Hälfte)?
- [ ] Welche Stufe fühlt sich am besten an: schnell genug, ohne ins Wort zu fallen?

## Block 7 – A5: Latenz, Deutsch, Grafikspeicher (8 Minuten)
- [ ] Claude: Latenz über die ganze Sitzung aus `sitzung_auswerten.py` (Median, höchster Wert), dazu aus dem
      Log der App „first audio delta“. Die Funkstrecke zum Reachy steckt in beiden nicht drin.
- [ ] Patrick: Fühlt sich die Wartezeit wie in einem Gespräch an? Grenzwert 1,5 s bestätigen oder ändern.
- [ ] Patrick, Deutsch der Antworten (Note 1 bis 5): Satzbau, Wortwahl, Aussprache, Betonung.
- [ ] Patrick: Stören die Ausrufezeichen hörbar (klingt sie aufgedreht)? In B4: 42 von 72 Antworten.
- [ ] Claude: Grafikspeicher je Prozess (`nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv`).
- [ ] Nur wenn Patrick es will und der Speicher reicht: größere Stimme 1.7B (rund 4 GB). Der Start damit
      ist nicht vorbereitet und nicht geprüft; das wäre ein eigener Schritt mit eigenem Ja.

## Block 8 – A6: eingeschleuste Sätze (10 Minuten)
Claude schickt Satz für Satz aus `tests/a4/say_saetze.txt`:
`~/lola-laufzeit/s2s-venv/bin/python tests/a4/say_schritt.py <Nummer>` (Mikrofon beim Senden kurz stumm).
Nach jedem Satz antwortet Patrick ein- bis zweimal ganz normal.
- [ ] Spricht LoLa den Inhalt in eigenen Worten und richtet ihn an Patrick?
- [ ] Oder antwortet sie, als hätte Patrick das gesagt („Okay, ich sage es ihm“)?
- [ ] Hilft die Kennzeichnung „[Hinweis, nicht von Patrick gesprochen]“ (Sätze 2, 3, 4, 6 gegen 1 und 5)?
- [ ] Geht das Gespräch danach sauber weiter, oder ist sie verwirrt, wer was gesagt hat?
- [ ] Einmal einen Satz schicken, während LoLa spricht: bricht sie ab und sagt den neuen Satz?
- [ ] Claude: Ging ein Satz verloren (Log der App, Neuverbindung)?

## Block 9 – Rest aus A7: Mithören mit zweitem Programm (3 Minuten)
- [ ] Claude startet den Mitleser aus `test/a7` für 60 Sekunden:
      `~/lola-laufzeit/app-venv/bin/python tests/a7/mitlesen.py 60 ~/lola-laufzeit/messung/a7/hoerprobe`
- [ ] Patrick redet währenddessen mit LoLa: Stottert der Ton, kommen Antworten später?

## Ende
- [ ] Patrick: „Geh jetzt schlafen.“ → legt sie sich hin (Tool `go_to_sleep`)?
- [ ] Claude: `uv run python -m dienste.lola_start stop`, danach prüfen: Motoren aus, Grafikspeicher frei.
- [ ] Claude: IMU-Temperatur und Motortemperaturen zum Schluss lesen (nur lesen), Daemon-Log auf Fehler.

## Danach entscheidet Patrick
1. Einstellung der Pausenerkennung (Block 6) – kommt dann fest in `lola_start`.
2. Weg 2 bestanden? Dann ARCHITEKTUR umstellen und die App auf dem Reachy deinstallieren.
3. Latenz-Grenzwert, Stimme 0.6B oder 1.7B (A5).
4. `conversation.say` so nutzen, mit stummem Mikrofon beim Senden (A6)?
5. Issues bei Pollen einreichen?

## Stufen für Block 6
Vorgemessen ohne Roboter mit künstlichen Stimmen (Tabelle in `MESSUNGEN.md`, 9. Oktober 2026).
Ergebnis dort: Die Rückhaltezeit zu senken macht nicht schneller, schneidet aber öfter ab.

| Stufe | Start | Erwartung aus der Vormessung |
| --- | --- | --- |
| A, Standard | `uv run python -m dienste.lola_start start` | „Ja.“ ohne Antwort; 0,7 s Pause schneidet manchmal ab |
| B, empfohlen | `uv run python tests/a4/starte_stufe.py --min_speech_ms 256` | „Ja.“ bekommt eine Antwort |
| C | `… starte_stufe.py --min_speech_ms 256 --speculative_reopen_ms 1200` | zusätzlich: 0,7 s Pause hält |
| D, nur bei Zeit | `… starte_stufe.py --min_speech_ms 256 --no_smart_turn` | Vergleich: hilft Smart Turn bei echtem „ähm“? |

Stufe A läuft schon in den Blöcken 1 bis 5, dort also nur auf „Ja.“ und Abschneiden achten.
Worauf es bei B besonders ankommt, weil es nicht vormessbar war:
- [ ] Springt LoLa auf Geräusche an (Husten, Tür, Geschirr, Fernseher), ohne dass jemand mit ihr spricht?
- [ ] Wird „Ja.“ als „Ja“ erkannt oder als „Yeah“?
