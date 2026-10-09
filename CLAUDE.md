# CLAUDE.md – Familien-Companion (Reachy Mini)

Diese Datei ist verbindlich. Lies sie zu Beginn jeder Sitzung ganz.
Sie bleibt unter 150 Zeilen. Details stehen in `docs/`, nicht hier.

**Aktuelle Phase:** 0 – Fundament und Messung. Nächster Auftrag: A6 am Roboter, danach B5 (siehe `docs/FAHRPLAN.md`).

## Projekt
Ein Reachy Mini Wireless soll als lebendig wirkendes Familienmitglied im Haushalt leben.
Pollens Conversation App liefert die Gesprächsschleife und bleibt unverändert.
Sprache und Sprachmodell laufen lokal auf dem NVIDIA-PC.
Unser Code: die Seele (Gefühl, Bedürfnisse, Beziehung, Gedächtnis), die Sinne, wenige Werkzeuge.

## Oberste Designregel
Ein neuer Baustein, eine neue Zustandsgröße oder eine neue Fähigkeit kommt nur hinzu,
wenn ein beobachtetes Verhalten ohne sie fehlt. Vorher testen, was ohne sie passiert.
Lieber streichen als ergänzen.

## Zusammenarbeit mit Patrick
- Patrick programmiert nicht selbst. Erkläre jeden Schritt vorher in einfachen Worten.
- Baue nichts ohne sein ausdrückliches Ja.
- Sprich Deutsch. Bezeichner deutsch, ohne Umlaute (`gedaechtnis`). Kommentare deutsch.
- Wenn eine Regel im Weg steht: Sag es ihm. Umgehe sie nie.
- Trenne klar zwischen Geprüftem und Vermutetem.

## Architektur (Details: `docs/ARCHITEKTUR.md`, Psychologie: `docs/KONZEPT.md`)
| Baustein | Ordner | Aufgabe |
|---|---|---|
| Seele | `seele/` | einziger Zustandshalter: Bewertung, Zustand, Beziehung, Gedächtnis, Auswahl |
| Sinne | `sinne/` | Rohdaten → Wahrnehmungen. Schreiben nie Zustand. |
| Vermittler | `vermittler/` | HTTP-Proxy zwischen speech-to-speech und llama.cpp. Meldet Gesagtes, startet die Deutung, setzt den Zustandsbericht als eigenen Eintrag vor den letzten Nutzersatz, entfernt Bewegungs-Tools bei harten Grenzen. Sonst reicht er unverändert durch. |
| Werkzeuge | `werkzeuge/` | Tools der Conversation App, eine Datei pro Tool |
| Dienste | `dienste/` | dauerhafte Hintergrunddienste (z. B. `waechter`) |

Nicht unser Code (nur Konfiguration, Version festgenagelt): Reachy-Daemon, Conversation App,
speech-to-speech, llama.cpp.

## Der Seelen-Kreislauf – unverletzlich
Wahrnehmung → Deutung → Bewertung → Zustand → Auswahl → Verhalten → (Ergebnis wird Wahrnehmung)

1. Ein Ereignis wird genau einmal bewertet, nur in `seele/bewertung.py`.
   Das Sprachmodell deutet nur (was meint die Person?), es bewertet nie.
2. Affekt, Stimmung und Bedürfnisse schreibt nur `seele/zustand.py`.
   Wer etwas ändern will, sendet eine Wahrnehmung.
3. Jeder Ereignistyp hat genau einen Absender. Alle Typen stehen in `seele/ereignisse.py`.
   Höchstens 30 Typen.
4. Persönlichkeit ist Konfiguration (`charakter/*.toml`), kein Modul und keine „Engine“.
5. Sichten (Erzählung, Selbstbild, Zustandsbericht) lesen nur.
6. Jede Zustandsänderung wird mit Auslöser ins Erklär-Log geschrieben.
7. `seele/` importiert weder `reachy_mini` noch Netzwerk-Bibliotheken. Sie ist ohne Hardware testbar.
8. Die Schutzregeln (`docs/KONZEPT.md`) gehen jeder Bewertung vor.

## Projektstruktur
```text
CLAUDE.md            diese Datei
README.md            Was ist das, wie starte ich es
.env.example         alle Einstellungen, ohne Geheimnisse (entsteht mit der ersten Einstellung)
charakter/           Charakterwerte als TOML
docs/                ARCHITEKTUR, KONZEPT, FAHRPLAN, ENTSCHEIDUNGEN, MESSUNGEN, BACKLOG, CHANGELOG
seele/               der Kern
sinne/               eine Datei pro Sinn
vermittler/          der Proxy
werkzeuge/           eine Datei pro Tool
dienste/             Hintergrunddienste
tests/               spiegelt die Ordner oben, Attrappen in tests/attrappen/
```
Neue Ordner auf oberster Ebene nur nach Eintrag in `docs/ENTSCHEIDUNGEN.md`.

## Wo gehört was hin?
| Ich will … | Ort |
|---|---|
| eine Fähigkeit, die das Sprachmodell aufruft | `werkzeuge/<name>.py` |
| eine neue Wahrnehmungsquelle | `sinne/<name>.py` |
| eine neue Bewertungsregel | `seele/bewertung.py` plus Test |
| einen Charakterwert | `charakter/*.toml` |
| eine Einstellung | `.env` und `.env.example` |
| ein Passwort oder einen Schlüssel | nur `.env`, nie ins Repo |
| eine Idee für später | `docs/BACKLOG.md` |
| eine Begründung | `docs/ENTSCHEIDUNGEN.md`, datiert |
| eine Messtabelle | `docs/MESSUNGEN.md`, in ENTSCHEIDUNGEN nur Ergebnis und Verweis |

## Budgets – bei Überschreitung anhalten und Patrick fragen
- Datei: höchstens 300 Zeilen. Funktion: höchstens 50 Zeilen. Werkzeug: höchstens 150 Zeilen.
- Die 300 Zeilen gelten nur für Code, nicht für Dokumente in `docs/`.
- Konfiguration (`.env.example`): höchstens 100 Zeilen.
- Ereignistypen: höchstens 30. Diese Datei: höchstens 150 Zeilen.

## Verboten
- Pollen-Code ändern, forken oder kopieren.
- Code aus Unit Sigma kopieren. Sigma liefert Ideen, keine Dateien. Ablauf je Modul: Sigma-Code nur
  außerhalb des Repos lesen → Steckbrief `docs/sigma/<modul>.md` (Verhalten, gute Idee, Ballast,
  was ohne fehlt) → Patricks Entscheidung → neu schreiben gegen KONZEPT, ohne Sigma-Namen.
- Neue Abhängigkeiten ohne Rückfrage.
- Toter Code, auskommentierter Code, Platzhalter, „TODO später“.
- Cloud als Standard. Cloud nur als Notlösung per `.env`, standardmäßig aus.
- Private Daten (Stimmabdrücke, Gesichter, Gedächtnis) außerhalb des Heimnetzes.
- Geheimnisse im Repo.
- Personen anlegen ohne Zustimmung, Kinder nur mit Zustimmung der Eltern.

## Ablauf jeder Sitzung
1. Lies diese Datei, `docs/ARCHITEKTUR.md` und die letzten Einträge in `docs/CHANGELOG.md`.
2. Patrick nennt genau eine Aufgabe aus dem Fahrplan.
3. Sag in drei Sätzen: was du tust, welche Dateien sich ändern, wie viele Zeilen ungefähr.
4. Erst nach seinem Ja (im Chat) baust du.
5. Gearbeitet wird immer auf dem Branch `entwicklung`. Kein eigener Branch pro Aufgabe, nie direkt auf `main`.
6. Gepusht wird nur, wenn `uv run pytest` und `uv run ruff check .` grün sind. Nie mit roten Tests pushen.
7. Changelog nachtragen, bei Bedarf die Entscheidung festhalten, committen, auf `entwicklung` pushen.
   Patrick sagt, wie es sich am Roboter verhält.
8. Nach `main` kommt nur etwas, wenn Patrick es ausdrücklich sagt („Stand sichern“, Ende einer Phase).
   Dann mergst du `entwicklung` selbst nach `main`. Nie halbfertiger Code auf `main`.
9. Patrick muss auf GitHub nichts tun. Du pushst und mergst selbst.
10. Ausnahme: Machbarkeitstests laufen in eigenen Branches (`test/...`) und werden nie gemergt.
    Nur das Ergebnis kommt nach `docs/ENTSCHEIDUNGEN.md`.

## Tests
- `uv run pytest` und `uv run ruff check .` müssen grün sein.
- Jede Bewertungsregel und jedes Werkzeug hat mindestens einen Test.
- Hardware und Sprachmodell werden in Tests durch Attrappen ersetzt.

## Fertig heißt
- [ ] Budgets eingehalten, Tests grün
- [ ] am echten Roboter geprüft
- [ ] Changelog und, wenn nötig, Entscheidungen aktualisiert
- [ ] README und Architektur stimmen noch
- [ ] Phasenabschluss: eine Woche Familienalltag bestanden, Git-Tag gesetzt (`v0.2`)

## Technik
Linux zuerst, Windows zweite Priorität: Code plattformneutral halten (`pathlib`, keine Shell-Tricks).
Python 3.12 · uv · ruff · pytest · SQLite.
Versionen von Reachy-SDK, Conversation App, speech-to-speech und llama.cpp
stehen in `docs/ENTSCHEIDUNGEN.md`. Upgrades sind eine eigene Aufgabe.
