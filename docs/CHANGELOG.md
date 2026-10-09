# Changelog

Neueste Einträge oben.

## 2026-10-09 – B4b: Steckbriefe aus Unit Sigma
- Neu: `docs/sigma/companion_dna.md`, `humor_engine.md`, `tracing.md` (Verhalten, gute Idee, Ballast, was
  fehlt, Vorschlag). Sigma liegt schreibgeschützt außerhalb des Repos, nichts daraus kopiert.
- Neu: `tests/test_kein_sigma_code.py` vergleicht unsere `.py`-Dateien mit allen in Sigma (Zeilen ab 40
  Zeichen, ohne Importe). Pfad über `LOLA_SIGMA` in `.env`; ohne Pfad wird der Test übersprungen.
- Entschieden: `companion_dna` verkleinern, `humor_engine` und `tracing` streichen. B5 um die Humor-Fragen
  ergänzt, Runden-Kennung im BACKLOG.

## 2026-10-09 – Pausenerkennung vorgemessen, Merkpunkte aus B4
- Pausenerkennung von speech-to-speech in neun Stufen gemessen (nur Schalter, kein Code). Tabelle in
  `MESSUNGEN.md`, Empfehlung in `ENTSCHEIDUNGEN.md`. Entscheidung am Roboter, `lola_start` unverändert.
- FAHRPLAN: Ausrufezeichen trotz Sprechanweisung (A5, B5) und Kamera-Aufruf (A4) als offene Punkte;
  Zwischenspeicher-Frage erledigt. BACKLOG: leere Zusage „ich notiere das“ bis zum Kalender geparkt.
- Ablauf für die Sitzung am Roboter liegt als Checkliste auf Branch `test/a4-pc`.

## 2026-10-09 – Ablauf für Unit-Sigma-Module, Auftrag B4b
- CLAUDE.md: Sigma-Module nur über Steckbrief und Neuschreiben übernehmen, nie kopieren.
- FAHRPLAN: B4b (Steckbriefe `companion_dna`, `humor_engine`, `tracing`) vor B5.

## 2026-10-09 – Entwürfe für Issues bei Pollen
- Neu: `docs/issues-entwuerfe.md` mit vier Entwürfen (Fundstelle, Schritte, Logs, AI-Angabe). Nicht eingereicht.

## 2026-10-09 – B4: Vermittler in der echten Kette (ohne Roboter)
- `dienste/lola_start.py` startet den Vermittler mit; speech-to-speech fragt jetzt ihn statt llama.cpp.
  Neue Aktion `kette`: alles außer der App, der Reachy bleibt unberührt.
- `wiederholt` im Anfrage-Log: gleiche Stelle im Gespräch und höchstens 5 s Abstand; die Folgeanfrage nach
  einem Tool-Ergebnis zählt nicht. Beides nach Messung an der echten Kette geändert.
- Gemessen: Zusatzzeit 0,7 ms, Zwischenspeicher hält, Tools 27 von 27 und 24 von 27, Abbruch nach rund 20 ms.
  Werte in `MESSUNGEN.md`, Ergebnis in `ENTSCHEIDUNGEN.md`. Probe am Roboter steht aus.

## 2026-10-09 – B3: Vermittler
- Neu: `vermittler/anfrage.py` (Bericht einsetzen, Tools entfernen) und `vermittler/proxy.py` (HTTP-Proxy
  mit Streaming und Abbruch, nur Standardbibliothek). Neu: Attrappe `tests/attrappen/llama.py`.
- Anfrage-Log kennzeichnet wiederholte und abgebrochene Anfragen; der Vermittler räumt beim Start auf.
- 31 neue Tests gegen die Attrappe. Noch nicht in der echten Kette (B4), `lola_start` unverändert.

## 2026-10-09 – Ursache der verlorenen `conversation.say`-Sätze
- Gefunden und nachgestellt: `say` sendet aus einem fremden Faden; mit stummem Mikrofon beim Senden kein
  Abbruch mehr. Ergebnis und Vorschlag in `ENTSCHEIDUNGEN.md`, Reihen in `MESSUNGEN.md`.
- BACKLOG: Issue für Pollen; Tonlücken und fehlendes `rtpgccbwe` vor Phase 3 prüfen. Kein Code geändert.

## 2026-10-09 – B2: Protokolle als Dateien
- `seele/erklaer_log.py` schreibt jeden Eintrag zusätzlich als Zeile JSON, wenn eine Datei angegeben ist.
- Neu: `vermittler/anfrage_log.py` mit Tagesdateien und Löschfrist (`LOLA_ANFRAGE_LOG_TAGE`, Standard 7).
- 13 neue Tests, die Löschfrist mit der Uhr-Attrappe. Noch nirgends angeschlossen (kommt mit B3).

## 2026-10-09 – B1: Zustandsbericht in der Form aus A3
- `seele/zustandsbericht.py`: eine Zeile mit Kennung `[Zustand]`, „Du, LoLa, bist …“, Sprechanweisung je
  Stufe aus derselben festen Tabelle. Kopfzeile und „Halte dich kurz“ entfallen.
- Tests: alle 20 Kombinationen der Stufen, keine Zahlen, keine Beispielsätze. Beispiel in `KONZEPT.md`.

## 2026-10-09 – A7: Machbarkeitstest Sinne
- Ein zweites Programm auf dem PC kann Ton und Bild des Reachy per WebRTC mitlesen, während die App läuft.
  Ergebnis in `ENTSCHEIDUNGEN.md`, Messwerte in `MESSUNGEN.md`, Fahrplan nachgezogen.
- Nebenbefund für A6: 2 von 14 eingeschleusten Sätzen gingen verloren. Kein Code auf `entwicklung` geändert.

## 2026-10-09 – Zwischenstand: Conversation App auf dem PC
- `dienste/lola_start.py` startet jetzt auch die Conversation App auf dem PC, prüft vorher den Reachy,
  setzt die Mikrofon-Werte und legt den Reachy beim Stoppen schlafen (Motoren aus). 14 Tests.
- Neu: `charakter/profile/lola_deutsch/profile.md` (Name LoLa). `.env.example`: `LOLA_REACHY`, `LOLA_PROFIL`.
- README: Startabschnitt angepasst. `ENTSCHEIDUNGEN.md`: Zwischenstand, Tests mit Patrick offen.
  `MESSUNGEN.md`: Motortemperaturen, Start und Grafikspeicher. `ARCHITEKTUR.md` bewusst noch unverändert.
- Am Roboter geprüft: Start, Begrüßung, Stopp mit Schlafhaltung. Gespräch mit Patrick steht aus.

## 2026-10-09 – A4: Startskript für die Sprachkette
- Neu: `dienste/lola_start.py` startet und stoppt llama.cpp und speech-to-speech, prüft, ob beide
  antworten, und nennt die Adresse für die App. Nur Standardbibliothek, 151 Zeilen, 6 Tests.
- Neu: `.env.example` mit drei Einstellungen. README: Abschnitt „So starte ich LoLa“.
- Am PC geprüft: Start in 21 s, Grafikspeicher 635 → 9.265 MiB, Stopp gibt alles frei.
- Mit dem Reachy noch nicht geprüft.

## 2026-10-09 – A4: Stände am Reachy festgenagelt
- Daemon 1.11.0, Conversation App 1.0.1 (`ddc3096`), Reachy Control 0.9.35. An der laufenden App geprüft.
- Fehler in der Update-Prüfung des Daemons gefunden und in `ENTSCHEIDUNGEN.md` beschrieben; Issue im Backlog.
- Regel: auf dem Reachy nur Apps, die wir nutzen.
- Korrigiert: Adresse des Daemon-Logs (`/logs/ws/daemon`) und Schalter `--stream_batch_sentences`.
- `ARCHITEKTUR.md`: Fakten zur App auf Stand 1.0.1 gebracht. Kein Code geändert.

## 2026-10-09 – Fahrplan Phase 2 in Aufträge C0 bis C8 aufgeteilt
- Werkzeug-Brücke, Timer, Kalender (Synology), App-Wechsel mit Ausstiegsgeste, Uhrzeit und Wetter lokal.
- BACKLOG: SearXNG, Ausstieg per Sprache, Storyteller. Entscheidung in ENTSCHEIDUNGEN.

## 2026-10-09 – Fahrplan Phase 1 in Aufträge B1 bis B6 aufgeteilt
- Phase 1 im FAHRPLAN mit sechs Aufträgen wie in Phase 0, Herkunft aus Unit Sigma benannt.

## 2026-10-08 – Sprachausgabe gewählt
- Qwen3-TTS 0.6B Base Q8_0 mit Referenzstimme „frau“, als gespeicherte Stimmdaten. Ersetzt „aiden“.
- Gemessen: 2.624 bis 2.722 MiB Grafikspeicher für den Prozess, Grenze 3 GB hält.
- 1.7B Base Q8_0 als Option für A5 im Fahrplan.
- Regel in `ENTSCHEIDUNGEN.md`: Referenzstimme einer realen Person nur mit Zustimmung, nur lokal.
  `.gitignore` schließt Stimmdaten (`*.spk`, `*.rvq`) aus.
- Messskript ergänzt auf Branch `test/a1`, nicht gemergt.
- A4 im Fahrplan: überlange Sprachausgaben (mehr als das Dreifache der erwarteten Dauer) mit Text und
  WAV mitschneiden; Stimmdaten nur in `~/lola-laufzeit/stimmen/` (Schalter für den Cache-Ordner).
- A5b „Sprachausgabe-Vergleich“ (F5-TTS, Fish Speech) aus dem Fahrplan gestrichen: mit der Wahl erledigt.

## 2026-10-08 – Nach A3: Entscheidungen eingearbeitet
- Der Zustandsbericht steht als eigener Eintrag vor dem letzten Nutzersatz: `CLAUDE.md`,
  `ARCHITEKTUR.md`, `ENTSCHEIDUNGEN.md`. Zwischenspeicher wird beim Bau des Vermittlers gemessen.
- Der Bericht darf eine Sprechanweisung enthalten, nur aus der festen Stufentabelle (`KONZEPT.md`).
- Der englische Mustersatz von speech-to-speech bleibt; der Vermittler reicht unverändert durch.
- Neu: `docs/MESSUNGEN.md` mit den Messtabellen aus A1 und A3. `ENTSCHEIDUNGEN.md` behält
  Ergebnis, Begründung und Verweis.
- `CLAUDE.md`, Budgets: Die 300 Zeilen gelten nur für Code, nicht für Dokumente.
- A4 im Fahrplan: Das deutsche Profil verbietet Emojis, leere Zusagen und erfundene Erinnerungen.
- Kein Code geändert.

## 2026-10-08 – A3: Machbarkeitstest Steuerbarkeit
- Englische Antworten kommen aus dem Standardprofil der App und dem Rahmen von speech-to-speech.
  Ein eigenes deutsches Profil (reine Daten) behebt das: 0 von 40 Antworten englisch.
- Bericht am Ende oder an der Nutzer-Nachricht stört die Tool-Aufrufe. Als Systemeintrag vor dem
  letzten Nutzersatz klappen 27 von 27.
- Der Ton folgt dem Bericht deutlich erst mit einem Satz, wie zu sprechen ist.
- Ergebnistabellen in `ENTSCHEIDUNGEN.md`, Skripte auf Branch `test/a3`, nicht gemergt.

## 2026-10-08 – A1 abgeschlossen
- Vorläufige Sprachausgabe: Qwen3-TTS 0.6B CustomVoice Q8_0, Stimme „aiden“. Klangurteil vertagt.
- Neue Aufgabe A5b „Sprachausgabe-Vergleich“ im Fahrplan (Referenzstimmen, F5-TTS, Fish Speech).
- Bündelung der Sprachausgabe: 1 Satz statt 3, als Einstellung in `ENTSCHEIDUNGEN.md`.
- `CLAUDE.md`: nächster Auftrag ist A3.

## 2026-10-08 – A1: Spracherkennung gewählt, Gesamtkette gemessen
- Spracherkennung: Parakeet TDT 0.6B v3 auf der CPU mit 6 Threads (0,26 s je Satz, Whisper 1,1 bis 5,1 s).
- Gesamtkette mit gespeicherten Aufnahmen: 0,50 s vom Satzende bis zum Antwortbeginn, 9,1 GB Grafikspeicher.
- Hinweise für A3 (Tool-Aufrufe, Englisch, Zustand der Person zugeschrieben) in `ENTSCHEIDUNGEN.md`.
- A4 um die 20 Testsätze über das Mikrofon des Reachy erweitert. Backlog: fester Puffer in qwentts.cpp.
- Offen in A1: nur noch das Klangurteil zur Stimme.

## 2026-10-08 – A1, Zwischenstand: Sprachausgabe und Nachprüfungen aus A2
- Hardware des PCs und Versionen (llama.cpp-Commit, Modell, Pakete) in `ENTSCHEIDUNGEN.md`.
- Sprachausgabe Qwen3-TTS gemessen: keine Variante unter 2 GB Grafikspeicher, auf der CPU zu langsam.
  Für A1 gilt 3 GB, A5 bewertet neu. Wahl der Variante offen (Klangurteil).
- Die sechs Nachprüfungen aus A2 gegen das echte llama.cpp beantwortet, alle bestanden. Zwei Nebenbefunde für A3.
- Offen in A1: Spracherkennung messen, Gesamtkette mit Mikrofon.

## 2026-10-08 – A1, Zwischenstand: Sprachmodell zum Start
- Qwen3-8B Q4_K_M als Startmodell für A1, Qwen3.5-9B und Gemma 4 12B als Kandidaten für A5.
- Qwen3.5 ist hybrid (Gated DeltaNet); Folge für den Zwischenspeicher in `ENTSCHEIDUNGEN.md` (gelesen, nicht gemessen).
- „Nicht nachdenken“ kommt bei llama.cpp mit dem Qwen3-Template an (gemessen).
- A1 bleibt offen. Messskripte auf Branch `test/a1`, nicht gemergt.

## 2026-10-08 – Docs mit den Live-Dokumenten abgeglichen
- Motortemperatur: möglicher Weg über `/api/move/ws/raw/write` (Register 146), Prüfung in A4 eingetragen.
- Akku und Motorschutz in ARCHITEKTUR und ENTSCHEIDUNGEN als im SDK-Code geprüft markiert (`fbdbca3`).

## 2026-10-08 – Phase 1, Kern ohne Hardware
- Erster Code: `pyproject.toml` (uv, Python 3.12, nur ruff und pytest), `charakter/reachy.toml`.
- `seele/charakter.py` lädt und prüft den Charakter, `seele/zustand.py` hält die Stimmung
  (Valenz, Erregung), `seele/erklaer_log.py` hält jede Änderung fest,
  `seele/zustandsbericht.py` baut den Bericht in Worten.
- 51 Tests, Uhr-Attrappe in `tests/attrappen/`.
- Docs: Akku-Bezüge entfernt, Motorschutz über das Daemon-Log beschrieben, Pollen-Issue im Backlog.

## 2026-10-08 – Arbeitsweise mit festem Branch `entwicklung`
- `CLAUDE.md`, Ablauf jeder Sitzung: immer auf `entwicklung`, `main` nur auf Patricks Freigabe,
  Push nur mit grünen Tests, Claude pusht und mergt selbst.
- Entscheidung dazu in `ENTSCHEIDUNGEN.md`.

## 2026-10-08 – A2: Machbarkeitstest Vermittler
- Ergebnis: geht mit Einschränkung, nur gegen eine Attrappe geprüft. Details in `ENTSCHEIDUNGEN.md`.
- Test-Code und Protokoll auf Branch `test/vermittler`, nicht gemergt.
- Nächster Auftrag: A1, dazu die Nachprüfungen aus A2.

## 2026-10-08 – A0: Repo-Gerüst
- `CLAUDE.md` mit Regeln, Struktur und Budgets.
- `docs/`: Architektur, Fahrplan, Konzept, Entscheidungen, Backlog, Changelog.
- `README.md`, `.gitignore`.
- Noch kein Code. Nächster Auftrag: A1 (lokale Sprachkette auf dem PC).
