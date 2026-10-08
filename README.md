# LoLa

Ein lebendig wirkender Familien-Companion auf dem Reachy Mini Wireless. Läuft lokal.

- **Körper und Stimme:** Pollens Reachy-Daemon und Conversation App, unverändert.
- **Gehirn:** ein Linux-PC mit NVIDIA-Grafikkarte, auf dem Sprachkette und Sprachmodell laufen.
- **Seele:** unser Code. Er gibt Reachy Stimmung, Bedürfnisse, Beziehungen und Gedächtnis.

## Wo steht was?

| Datei | Inhalt |
| --- | --- |
| `CLAUDE.md` | verbindliche Regeln für jede Arbeitssitzung |
| `docs/ARCHITEKTUR.md` | Bausteine und wie sie zusammenhängen |
| `docs/KONZEPT.md` | das psychologische Modell |
| `docs/FAHRPLAN.md` | Phasen und nächste Arbeitsaufträge |
| `docs/ENTSCHEIDUNGEN.md` | Entscheidungen mit Begründung, festgenagelte Versionen |
| `docs/MESSUNGEN.md` | Messtabellen aus den Machbarkeitstests |
| `docs/BACKLOG.md` | Ideen für später |
| `docs/CHANGELOG.md` | was sich wann geändert hat |

## Stand

Phase 0, Fundament und Messung. Dazu vorgezogen der Kern von Phase 1 ohne Hardware:
Charakter, Grundzustand, Zustandsbericht und Erklär-Log. Noch nichts zu starten.

Tests und Prüfung (braucht [uv](https://docs.astral.sh/uv/)):

```bash
uv run pytest
uv run ruff check .
```

## Lizenz

Siehe `LICENSE`.
