# Fahrplan

Stand: 8. Oktober 2026. Quelle: Live-Dokument „Familien-Companion – Architektur & Fahrplan“
(https://claude.ai/code/artifact/e1370057-a130-448d-8bc3-b9fd9f31aa50).

Neun Phasen, jede mit einem Abnahmekriterium. Die Seele wächst von innen nach außen:
erst wer spricht und was Reachy weiß, dann Gefühl, dann Beziehung, dann Eigeninitiative.

## Phase 0 – Fundament und Messung

Arbeitsaufträge, je einer pro Sitzung. A0 bis A3 brauchen den Roboter nicht.

| # | Auftrag | Roboter nötig | Ergebnis |
| --- | --- | --- | --- |
| A0 | Repo-Gerüst: CLAUDE.md, `docs/`, README, `.gitignore` | nein | erledigt am 8. Oktober 2026 |
| A1 | Lokale Sprachkette auf dem PC: speech-to-speech und llama.cpp, deutsche Spracherkennung (Parakeet gegen faster-whisper), Qwen3-TTS mit deutscher Stimme. Test mit dem Mikrofon des PCs. | nein | erledigt am 8. Oktober 2026, ohne Mikrofon mit gespeicherten Aufnahmen: 0,50 s vom Satzende bis zum Antwortbeginn, 9,1 GB Grafikspeicher. Sprachausgabe: Qwen3-TTS 0.6B Base Q8_0 mit Referenzstimme „frau“, siehe `ENTSCHEIDUNGEN.md` |
| A2 | Machbarkeitstest Vermittler: Reicht ein Proxy zwischen speech-to-speech und llama.cpp Anfragen samt Tools unverändert durch? Lassen sich Tools pro Anfrage entfernen? | nein | geht (8. Oktober 2026), in A1 gegen das echte llama.cpp nachgeprüft; siehe `ENTSCHEIDUNGEN.md` |
| A3 | Machbarkeitstest Steuerbarkeit: Folgt das Modell einem festen Zustandsbericht (etwa „müde und zurückhaltend“) bei 20 Testsätzen? | nein | erledigt am 8. Oktober 2026: geht, wenn der Bericht vor dem letzten Nutzersatz steht und sagt, wie zu sprechen ist; deutsches Profil nötig. Siehe `ENTSCHEIDUNGEN.md` |
| A4 | Reachy mit der lokalen Sprachkette verbinden, Versionen von Daemon, SDK und App festhalten. Dazu Körperdaten prüfen: Fehlerzeilen im Daemon-Log (`/api/logs/ws/daemon`), IMU-Temperatur, und ob ein Lese-Paket für Register 146 (Motortemperatur) über `/api/move/ws/raw/write` bei laufender App sauber antwortet. Eigenes deutsches Profil als Daten laden (A3): immer Deutsch, kurz, Tool sofort ohne Vorrede, keine Beispielsätze, keine Emojis, keine Zusagen für Fähigkeiten, die Reachy nicht hat, keine erfundenen Erinnerungen; prüfen, ob das Modell sich daran hält. Sprachausgabe mit gespeicherten Stimmdaten und `--qwen3_tts_ref_cache_dir ~/lola-laufzeit/stimmen/` starten. Jede Sprachausgabe, die länger als das Dreifache der erwarteten Dauer ist (erwartet: rund 16 Zeichen je Sekunde, aus A1), mit Text und WAV mitschneiden, lokal in `~/lola-laufzeit/`. Dazu die 20 Testsätze aus A1 über das Mikrofon des Reachy: Wortfehler von Parakeet, und ob es bei kurzen Sätzen („Ja.“, „Stopp!“) die Sprache verwechselt | ja | Reachy spricht über das lokale Backend, Ergebnis Körperdaten in `ENTSCHEIDUNGEN.md` |
| A5 | Latenz bis Antwortbeginn, Deutsch-Qualität und Grafikspeicher messen. Falls Speicher übrig ist: Sprachausgabe 1.7B Base Q8_0 (rund 4 GB) als Option prüfen | ja | Entscheidung: weiter oder Backend wechseln |
| A6 | Machbarkeitstest `conversation.say`: Wie formuliert das Modell eine eingeschleuste Äußerung, entsteht daraus über mehrere Runden ein sauberes Gespräch? | ja | Ergebnis in `ENTSCHEIDUNGEN.md` |
| A7 | Machbarkeitstest Sinne: Kann ein Programm auf dem PC Mikrofon und Kamerastrom parallel zur laufenden App lesen, ohne sie zu stören? | ja | Ergebnis in `ENTSCHEIDUNGEN.md` |

Machbarkeitstests laufen in eigenen Branches und kommen nicht nach `main`.
Nur das Ergebnis wird in `docs/ENTSCHEIDUNGEN.md` festgehalten.

*Abnahme:* höchstens 1,5 s bis zum Antwortbeginn auf Deutsch (Grenzwert noch zu bestätigen),
alle Machbarkeitstests bestanden.

## Phase 1 – Seelen-Skelett

Ziel: Reachy spricht mit einer festen, erkennbaren Persönlichkeit. Der Vermittler steht zwischen
speech-to-speech und llama.cpp und legt in jede Anfrage den Zustandsbericht. Noch ohne Gefühl
und Bewertung (Phase 4): Der Zustand ändert sich in Phase 1 nicht, er kommt aus der Charakterdatei.

Aus Unit Sigma (nur Ideen, kein Code): `companion_dna` und `humor_engine` werden zur
Charakterdatei, `tracing` wird zum Erklär-Log. Ein Humor-Wert kommt nur hinzu, wenn B5 zeigt,
dass er fehlt (oberste Designregel).

Vorgezogen am 8. Oktober 2026 (ohne Hardware): Charakterdatei mit Lader, Grundzustand,
Zustandsbericht, Erklär-Log im Speicher, Tests.

| # | Auftrag | Roboter nötig | Ergebnis |
| --- | --- | --- | --- |
| B1 | Zustandsbericht in die Form aus A3 bringen: eigener Eintrag mit Kennung `[Zustand]`, „Du, Reachy, bist …“, dazu eine Sprechanweisung je Stufe (z. B. „Sprich ruhig und knapp, ohne Ausrufezeichen“). Eine feste Tabelle in `seele/zustandsbericht.py`, keine freien Texte, keine Beispielsätze. Beispiel in `KONZEPT.md` nachziehen | nein (Cloud geht) | Bericht wie in A3 gemessen, Tests grün |
| B2 | Protokolle in Dateien: Erklär-Log (Zustandsänderungen) und Anfrage-Log (je Anfrage: Zeit, eingefügter Bericht, entfernte Tools, Dauer). Eine Zeile JSON je Eintrag, Ordner `daten/` (nicht im Repo). Das Anfrage-Log enthält Gesagtes der Familie: nur lokal, nach 7 Tagen automatisch gelöscht, Frist in `.env` | nein (Cloud geht) | Logs nachlesbar, Löschfrist getestet |
| B3 | Vermittler bauen (`vermittler/`): HTTP-Proxy für `/v1/responses` mit Streaming und Abbruch, setzt den Bericht vor den letzten Nutzersatz, reicht sonst alles unverändert durch, schreibt das Anfrage-Log. Grundlage ist das Ergebnis aus A2, nicht dessen Code. Neue Abhängigkeit (HTTP-Bibliothek) nur nach Rückfrage. Tests gegen eine Attrappe von llama.cpp | nein (Cloud geht) | Vermittler läuft gegen die Attrappe, Tests grün |
| B4 | Vermittler in die echte Kette: speech-to-speech zeigt auf den Vermittler, `lola-start` startet ihn mit. Messen: Zwischenspeicher an der neuen Position (offene Frage), Zusatzzeit durch den Vermittler (Ziel unter 20 ms), Tool-Aufrufe wie in A3 | ja (nach A4) | Messwerte in `MESSUNGEN.md`, Kette läuft mit Vermittler |
| B5 | Persönlichkeitstest: zwei Charakterdateien mit deutlichem Unterschied (z. B. gesellig/neugierig gegen zurückhaltend/vorsichtig), je 15 Minuten Gespräch, ohne zu sagen, welche läuft. Erkennt die Familie den Unterschied? Wenn nicht: Bericht schärfen oder Werte streichen. Fehlt erkennbar Humor: erst dann einen Humor-Wert ergänzen | ja | Ergebnis in `ENTSCHEIDUNGEN.md`, endgültige Charakterwerte |
| B6 | Phasenabschluss: eine Woche Familienalltag mit Vermittler und Profil. Auffälligkeiten aus dem Anfrage-Log auswerten. Danach „Stand sichern“: `entwicklung` nach `main`, Git-Tag `v0.1` | ja | Phase 1 abgeschlossen |

Reihenfolge: B1 bis B3 brauchen weder Roboter noch PC und können laufen, während Phase 0
(A4 bis A7) am Roboter weitergeht. B4 setzt A4 voraus. B5 und B6 brauchen die ganze Kette.

*Abnahme:* Reachy hat eine erkennbare Persönlichkeit (B5), jede Anfrage ans Modell ist im Log
nachlesbar (B2), der Vermittler kostet unter 20 ms und bricht weder Tools noch Zwischenspeicher (B4).

## Phase 2 – Haushalt

Ziel: kleine Alltagsfähigkeiten (Timer, Kalender, Wetter), Wechsel zu anderen Apps mit sicherem
Rückweg, erste Eigeninitiative. Entschieden am 9. Oktober 2026 (Begründung in `ENTSCHEIDUNGEN.md`):

- **Werkzeuge:** externe Werkzeuge der Conversation App (`REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY`).
  Auf dem Reachy liegen nur dünne Hüllen (`werkzeuge/`), die den PC fragen. Logik und Passwörter
  liegen im `dienste/werkzeugdienst` auf dem PC. Tool Spaces von Hugging Face (nur `*.hf.space`)
  sind für Privates tabu.
- **Hintergrund:** Die App führt jedes Werkzeug im Hintergrund aus und meldet das Ergebnis ans
  Sprachmodell, sobald es fertig ist (bis zu einem Tag). `task_status` und `task_cancel` gibt es schon.
- **App-Wechsel:** Start über `POST /api/apps/start-app/{name}`. Der Rückweg ist für alle Apps gleich
  und verändert keine App: Der Wächter auf dem PC liest den Zustandsstrom
  `ws://reachy:8000/api/state/ws/full` (IMU) und erkennt eine Ausstiegsgeste (zweimal oben auf den
  Kopf tippen). Dann stoppt er die laufende App und startet die Conversation App. Antennen sind keine
  Geste, die Radio-App nutzt sie selbst. Apps von Pollen werden nicht kopiert. Eigene Apps
  (z. B. der Storyteller) liegen in `apps/` und müssen sich nur sauber beenden können.
- **Uhrzeit** steht im Zustandsbericht, ohne Werkzeug. **Wetter** über Open-Meteo vom PC aus
  (ohne Konto, Ort in `.env`).

| # | Auftrag | Roboter nötig | Ergebnis |
| --- | --- | --- | --- |
| C0 | Machbarkeitstests (Branch `test/c0`): (a) externer Werkzeug-Ordner auf dem Reachy setzbar (Datei auf dem Roboter, nur mit Ja), (b) eine Hülle ruft einen Dienst auf dem PC, (c) Ergebnis eines Hintergrund-Werkzeugs nach 2 Minuten wird angesagt, auch wenn gerade niemand spricht, (d) Ausstiegsgeste: Ist zweimaliges Antippen im IMU-Strom sicher erkennbar, ohne Fehlauslösung durch Tanz, Emotionen oder Kopfbewegungen? | ja | Ergebnis in `ENTSCHEIDUNGEN.md` |
| C1 | Werkzeug-Brücke: `dienste/werkzeugdienst` auf dem PC (nur im Heimnetz erreichbar, Schlüssel in `.env`), eine Hülle je Werkzeug auf dem Reachy. Ist der PC aus, antwortet die Hülle freundlich mit einem Fehler. `lola-start` startet den Dienst mit | ja | ein Test-Werkzeug läuft über die Brücke |
| C2 | Timer als Hintergrund-Werkzeug (stellen, „wie lange noch?“, abbrechen über `task_status`/`task_cancel`). Testen, ob ein Timer einen App-Wechsel überlebt; wenn nicht, wandert er in den Werkzeugdienst und meldet sich über `conversation.say` | ja | Timer im Alltag nutzbar |
| C3 | Kalender lesen: Synology Calendar über CalDAV, inkl. wiederkehrender Termine. Abhängigkeit (vermutlich `caldav`, `icalendar`) nur nach Rückfrage, nur auf dem PC. Zugangsdaten nur in `.env` | ja | „Was steht morgen an?“ klappt |
| C4 | Kalender eintragen mit Bestätigung: Das Werkzeug liefert erst einen Vorschlag („Donnerstag 18 Uhr Fußballtraining, eintragen?“), eingetragen wird erst nach einem Ja. Kein Löschen per Sprache | ja | Eintrag mit Bestätigung klappt |
| C5 | App-Wechsel: Werkzeug `app_starten` (nur Apps aus einer festen Liste in `.env`), `dienste/waechter` mit Ausstiegsgeste aus C0. Der Wächter startet die Conversation App nur neu, wenn er die andere App selbst gestartet hat (nicht nach „geh schlafen“). Ordner `apps/` anlegen (Eintrag in `ENTSCHEIDUNGEN.md`) | ja | Radio hin und per Antippen zurück |
| C6 | Datum und Uhrzeit in den Zustandsbericht (Pollen-Uhrzeit-Werkzeug abschalten). Wetter-Werkzeug über Open-Meteo im Werkzeugdienst (Pollen-Wetter-Werkzeug abschalten) | ja | Uhrzeit und Wetter ohne Hugging Face |
| C7 | Erste Eigeninitiative: einfache Gesichtserkennung (nur „Gesicht erschienen / verschwunden“, kein Erkennen der Person) lässt Reachy über `conversation.say` grüßen. Höchstens einmal pro Stunde und Person-unabhängig, nie während jemand spricht, nicht nachts. Setzt A6 und A7 voraus | ja | Reachy grüßt, nervt aber nicht |
| C8 | Phasenabschluss: eine Woche fehlerfreier Betrieb, dann „Stand sichern“ und Git-Tag `v0.2` | ja | Phase 2 abgeschlossen |

Reihenfolge: C0 zuerst; C1 vor C2 bis C6. C7 braucht A6 und A7 aus Phase 0.

*Abnahme:* Timer, Kalender (lesen und eintragen), Wetter und Uhrzeit funktionieren lokal; Radio hin
und per Antippen zurück; Reachy grüßt von sich aus mit Obergrenze; eine Woche fehlerfreier Betrieb.

## Phase 3 – Wer spricht, was weiß ich?
- Sprechererkennung über die Stimme. Personen nur mit Zustimmung, Kinder nur mit Zustimmung der Eltern.
- Fakten, Zusagen und Episoden pro Person, vollständiges Vergessen auf Wunsch.
- *Abnahme:* Reachy erkennt jedes Familienmitglied und erinnert sich nach einem Neustart.

## Phase 4 – Gefühl
- Schnelle Bewertung und Deutung, Affekt, Stimmung, Bedürfnisse, harte Grenzen.
- Körperwahrnehmung (Motorfehler aus dem Daemon-Log, IMU-Temperatur), Tageszeit (daraus Müdigkeit), Leerlauf.
- *Abnahme:* Die Stimmung reagiert nachvollziehbar, jede Änderung lässt sich im Log auf ein Ereignis zurückführen.

## Phase 5 – Beziehung
- Beziehung pro Person aus Erwartungen („reagiert auf mich“, „hält Wort“), dazu das Selbstbild.

## Phase 6 – Sinne
- Akustische Ortung: Der Kopf dreht sich zum Sprecher.
- Geräusche (Lachen, Weinen, Türklingel), Stimmlage, Gesichter wiedererkennen (wer ist das?).

## Phase 7 – Eigeninitiative
- Die Auswahl löst Äußerungen über `conversation.say` aus, mit Obergrenze pro Stunde und nie,
  während jemand spricht.
- Neugier und Themenwechsel als Regeln.
- Nächtliche Nachbewertung, nur für ungeklärte und wichtige Episoden.

## Phase 8 – Tiefe
- Storyteller: zuerst Reachy Stories von Pollen auf Deutsch testen, sonst ein eigenes Profil.
- Haltung als dauerhafte Körpersprache aus der Stimmung. Reihenfolge: erst ein Issue bei Pollen,
  das um einen Haken für die Atem-Haltung bittet; sonst ein eigenes Werkzeug, das im
  App-Prozess mitläuft; nie ein Fork.
- „Unsere Geschichte“ als Lesesicht.

## Offene Fragen und Risiken

- [ ] Reichen 12 GB VRAM (RTX 3080 Ti) für Spracherkennung, Sprachmodell, Sprachausgabe und
      den parallelen Deutungs-Aufruf? Grobe Schätzung: knapp. Misst A5.
- [ ] Wie gut ist die deutsche Spracherkennung und -ausgabe? Zeiten in A1 gemessen. Die Fehlerquote
      der Erkennung mit echten Stimmen misst A4, die Stimme ist gewählt („frau“, 0.6B Base Q8_0).
- [ ] Verwechselt Parakeet bei kurzen Sätzen die Sprache? In A1 mit künstlicher Stimme „Yeah.“ statt
      „Ja.“. Es lässt sich nicht auf Deutsch festlegen. Klärt A4.
- [x] Sind die Tool-Aufrufe von Qwen3-8B verlässlich, und stört der Zustandsbericht sie? A3: Am Ende
      der Anfrage stört er, vor dem letzten Nutzersatz nicht (27 von 27).
- [x] Wo steht der Bericht? Entschieden: als eigener Eintrag vor dem letzten Nutzersatz (A3).
- [ ] Hält der Zwischenspeicher von llama.cpp an dieser Position? Vermutet, nicht gemessen.
      Messen, wenn der Vermittler gebaut wird (Phase 1).
- [x] Soll der Vermittler den englischen Mustersatz im Rahmen von speech-to-speech ersetzen?
      Entschieden: vorerst nein. Option mit Messwert (21 → 27 von 27) in `ENTSCHEIDUNGEN.md`.
- [ ] Antworten enthalten Emojis, erfundene Erinnerungen und leere Zusagen (A3). Das deutsche
      Profil verbietet sie; ob das wirkt und ob die Sprachausgabe Emojis vorliest, prüft A4.
- [ ] Hybride Modelle (Qwen3.5): Nutzt llama.cpp den Zwischenspeicher, wenn sich der Bericht kurz
      vor dem Ende ändert? Misst A5, bevor Qwen3.5 gewählt wird.
- [ ] Sprachausgabe braucht 2,6 bis 2,7 GB statt der geplanten 2 GB. Die Grenze ist 3 GB, A5 bewertet neu.
- [ ] Kann ein zweiter Prozess Mikrofon und Kamera parallel zur App lesen? Klärt A7.
- [ ] Körpersprache aus der Stimmung: siehe Phase 8.
- [ ] Grenzwert für die Latenz bestätigen. Vorschlag: 1,5 s.

- **Risiko PC aus:** Ohne den PC kann Reachy nicht sprechen. Notlösung: per `.env` auf ein
  Cloud-Backend umschalten, standardmäßig aus.
- **Risiko Updates:** Der Vermittler hängt an der Schnittstelle von speech-to-speech.
  Versionen festnageln, Upgrades nur bewusst.
- **Risiko Kinder und Daten:** Stimmabdrücke und Gesichter sind biometrische Daten.
  Sie bleiben lokal und verschlüsselt, jede Person kann vollständig gelöscht werden.
