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
| A1 | Lokale Sprachkette auf dem PC: speech-to-speech und llama.cpp, deutsche Spracherkennung (Parakeet gegen faster-whisper), Qwen3-TTS mit deutscher Stimme. Test mit dem Mikrofon des PCs. | nein | erledigt am 8. Oktober 2026, ohne Mikrofon mit gespeicherten Aufnahmen: 0,50 s vom Satzende bis zum Antwortbeginn, 9,1 GB Grafikspeicher. Stimme vorläufig, siehe `ENTSCHEIDUNGEN.md` |
| A2 | Machbarkeitstest Vermittler: Reicht ein Proxy zwischen speech-to-speech und llama.cpp Anfragen samt Tools unverändert durch? Lassen sich Tools pro Anfrage entfernen? | nein | geht (8. Oktober 2026), in A1 gegen das echte llama.cpp nachgeprüft; siehe `ENTSCHEIDUNGEN.md` |
| A3 | Machbarkeitstest Steuerbarkeit: Folgt das Modell einem festen Zustandsbericht (etwa „müde und zurückhaltend“) bei 20 Testsätzen? | nein | erledigt am 8. Oktober 2026: geht, wenn der Bericht vor dem letzten Nutzersatz steht und sagt, wie zu sprechen ist; deutsches Profil nötig. Siehe `ENTSCHEIDUNGEN.md` |
| A4 | Reachy mit der lokalen Sprachkette verbinden, Versionen von Daemon, SDK und App festhalten. Dazu Körperdaten prüfen: Fehlerzeilen im Daemon-Log (`/api/logs/ws/daemon`), IMU-Temperatur, und ob ein Lese-Paket für Register 146 (Motortemperatur) über `/api/move/ws/raw/write` bei laufender App sauber antwortet. Eigenes deutsches Profil als Daten laden (A3). Dazu die 20 Testsätze aus A1 über das Mikrofon des Reachy: Wortfehler von Parakeet, und ob es bei kurzen Sätzen („Ja.“, „Stopp!“) die Sprache verwechselt | ja | Reachy spricht über das lokale Backend, Ergebnis Körperdaten in `ENTSCHEIDUNGEN.md` |
| A5 | Latenz bis Antwortbeginn, Deutsch-Qualität und Grafikspeicher messen | ja | Entscheidung: weiter oder Backend wechseln |
| A5b | Sprachausgabe-Vergleich: Qwen3-TTS mit Patricks Referenzstimmen, F5-TTS und Fish Speech über den `openai_compatible`-Anschluss von speech-to-speech. Klang, Grafikspeicher, Zeit bis zum ersten Ton | ja | endgültige Stimme in `ENTSCHEIDUNGEN.md` |
| A6 | Machbarkeitstest `conversation.say`: Wie formuliert das Modell eine eingeschleuste Äußerung, entsteht daraus über mehrere Runden ein sauberes Gespräch? | ja | Ergebnis in `ENTSCHEIDUNGEN.md` |
| A7 | Machbarkeitstest Sinne: Kann ein Programm auf dem PC Mikrofon und Kamerastrom parallel zur laufenden App lesen, ohne sie zu stören? | ja | Ergebnis in `ENTSCHEIDUNGEN.md` |

Machbarkeitstests laufen in eigenen Branches und kommen nicht nach `main`.
Nur das Ergebnis wird in `docs/ENTSCHEIDUNGEN.md` festgehalten.

*Abnahme:* höchstens 1,5 s bis zum Antwortbeginn auf Deutsch (Grenzwert noch zu bestätigen),
alle Machbarkeitstests bestanden.

## Phase 1 – Seelen-Skelett
- Der Vermittler reicht alles durch und fügt einen festen Zustandsbericht aus der
  Charakterdatei hinzu. Dazu kommt das Erklär-Log.
- Vorgezogen am 8. Oktober 2026 (ohne Hardware): Charakterdatei mit Lader, Grundzustand,
  Zustandsbericht, Erklär-Log im Speicher, Tests. Offen: Vermittler, Log in eine Datei.
- *Abnahme:* Reachy hat eine erkennbare Persönlichkeit, jede Anfrage ans Modell ist im Log nachlesbar.

## Phase 2 – Haushalt
- Timer bauen. Kalender lesen und eintragen per CalDAV, mit mündlicher Bestätigung.
- App-Wechsel zum Radio, dazu der Wächter für den Rückweg.
- Erste Eigeninitiative: Eine einfache Gesichtserkennung (nur „Gesicht erschienen / verschwunden“,
  kein Erkennen der Person) lässt Reachy über `conversation.say` grüßen. Mit Obergrenze,
  nie während jemand spricht, nicht nachts.
- *Abnahme:* eine Woche fehlerfreier Betrieb.

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
      der Erkennung mit echten Stimmen misst A4, die Stimme wählt der Sprachausgabe-Vergleich (A5b).
- [ ] Verwechselt Parakeet bei kurzen Sätzen die Sprache? In A1 mit künstlicher Stimme „Yeah.“ statt
      „Ja.“. Es lässt sich nicht auf Deutsch festlegen. Klärt A4.
- [x] Sind die Tool-Aufrufe von Qwen3-8B verlässlich, und stört der Zustandsbericht sie? A3: Am Ende
      der Anfrage stört er, vor dem letzten Nutzersatz nicht (27 von 27).
- [ ] Der Bericht soll vor den letzten Nutzersatz statt ans Ende (A3). `ARCHITEKTUR.md` sagt noch
      „ans Ende“; Patrick entscheidet. Zwischenspeicher an dieser Position messen (A5).
- [ ] Soll der Vermittler den englischen Mustersatz im Rahmen von speech-to-speech ersetzen? Ohne
      Bericht im neuen Gespräch sonst nur 21 von 27 Tool-Aufrufen (A3).
- [ ] Antworten enthalten Emojis, erfundene Erinnerungen und leere Zusagen (A3). Prüfen in A4/A5.
- [ ] Hybride Modelle (Qwen3.5): Nutzt llama.cpp den Zwischenspeicher, wenn sich der Bericht am Ende
      ändert? Misst A5, bevor Qwen3.5 gewählt wird.
- [ ] Sprachausgabe braucht 2,5 GB statt der geplanten 2 GB. Für A1 gilt 3 GB, A5 bewertet neu.
- [ ] Kann ein zweiter Prozess Mikrofon und Kamera parallel zur App lesen? Klärt A7.
- [ ] Körpersprache aus der Stimmung: siehe Phase 8.
- [ ] Grenzwert für die Latenz bestätigen. Vorschlag: 1,5 s.

- **Risiko PC aus:** Ohne den PC kann Reachy nicht sprechen. Notlösung: per `.env` auf ein
  Cloud-Backend umschalten, standardmäßig aus.
- **Risiko Updates:** Der Vermittler hängt an der Schnittstelle von speech-to-speech.
  Versionen festnageln, Upgrades nur bewusst.
- **Risiko Kinder und Daten:** Stimmabdrücke und Gesichter sind biometrische Daten.
  Sie bleiben lokal und verschlüsselt, jede Person kann vollständig gelöscht werden.
