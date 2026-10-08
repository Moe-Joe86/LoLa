# Changelog

Neueste Einträge oben.

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
