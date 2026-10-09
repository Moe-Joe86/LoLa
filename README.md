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

Voraussetzung: Im Ordner `~/lola-laufzeit/` liegen llama.cpp, speech-to-speech, das Sprachmodell und
die Stimmdaten (Versionen in `docs/ENTSCHEIDUNGEN.md`). Abweichende Pfade stehen in `.env`,
Vorlage ist `.env.example`.

1. Auf dem PC, im Ordner dieses Repos, die Sprachkette starten (dauert rund 20 Sekunden):

   ```bash
   uv run python -m dienste.lola_start start
   ```

   Am Ende steht dort, welche Adresse in die App gehört, zum Beispiel `pop-os.local`, Port 8765.
2. Reachy einschalten und in Reachy Control die Conversation App starten.
3. Nur beim ersten Mal: in den Einstellungen der App unter „Connection“ auf „Local“ stellen und
   Host und Port aus Schritt 1 eintragen.
4. Beenden: die App in Reachy Control stoppen, dann auf dem PC:

   ```bash
   uv run python -m dienste.lola_start stop
   ```

Klappt der Start nicht, steht der Grund in `~/lola-laufzeit/lauf/sprachmodell.log` oder
`sprachkette.log`. Die Sprachkette belegt rund 8,6 GB Grafikspeicher.

Tests und Prüfung (braucht [uv](https://docs.astral.sh/uv/)):

```bash
uv run pytest
uv run ruff check .
```

## Lizenz

Siehe `LICENSE`.
