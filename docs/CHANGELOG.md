# Changelog

Neueste Einträge oben.

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
