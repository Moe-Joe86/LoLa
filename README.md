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
Charakter, Grundzustand, Zustandsbericht und Erklär-Log.

## So starte ich LoLa

Zwischenstand vom 9. Oktober 2026: Die Conversation App läuft auf dem PC, der Reachy ist nur Körper.
Der Test mit Patrick am Roboter steht noch aus.

Voraussetzung: Im Ordner `~/lola-laufzeit/` liegen llama.cpp, speech-to-speech, die Conversation App,
das Sprachmodell und die Stimmdaten (Versionen in `docs/ENTSCHEIDUNGEN.md`). Abweichende Pfade stehen
in `.env`, Vorlage ist `.env.example`.

1. Reachy einschalten. Auf ihm darf keine App laufen.
2. Auf dem PC, im Ordner dieses Repos (dauert rund 20 Sekunden):

   ```bash
   uv run python -m dienste.lola_start start
   ```

   Der Reachy wacht auf und LoLa begrüßt dich.
3. Beenden:

   ```bash
   uv run python -m dienste.lola_start stop
   ```

   Der Reachy legt sich schlafen, die Motoren gehen aus.

Klappt der Start nicht, steht der Grund in `~/lola-laufzeit/lauf/` (`sprachmodell.log`,
`sprachkette.log`, `app.log`). LoLa belegt rund 9 GB Grafikspeicher.

Tests und Prüfung (braucht [uv](https://docs.astral.sh/uv/)):

```bash
uv run pytest
uv run ruff check .
```

## Lizenz

Siehe `LICENSE`.
