# Changelog

Neueste Einträge oben.

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
