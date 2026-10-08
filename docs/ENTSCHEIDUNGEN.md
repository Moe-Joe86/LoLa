# Entscheidungen

Jede Architekturentscheidung mit Datum und Begründung. Neueste unten.
Wer später fragt „warum so?“, findet hier die Antwort.

## 2026-10-07 – Neustart statt Unit Sigma weiterbauen
Sigma hatte über 100.000 Zeilen, eine Konfiguration mit über 6.000 Zeilen und neun Module,
die gleichzeitig an der Stimmung schrieben. Sigma bleibt Ideenquelle, kein Code wird übernommen.

## 2026-10-07 – Basis: Pollens Conversation App, unverändert
Offiziell, aktiv gepflegt, erweiterbar über Profile, externe Tools und `/rpc`.
Kein Fork, keine Kopie: Jedes Pollen-Update würde sonst zum Konflikt.
Goshi verworfen: Deutsch nicht beworben, eigener Go-Server.

## 2026-10-07 – Lokal zuerst
Sprachkette und Sprachmodell laufen auf dem eigenen PC (RTX 3080 Ti, 12 GB VRAM).
Cloud nur als per `.env` abschaltbare Notlösung. Biometrie und Gedächtnis bleiben im Heimnetz.

## 2026-10-07 – Seele als eigener Dienst, angebunden über einen Vermittler
Der Vermittler sitzt zwischen speech-to-speech und llama.cpp und gibt jeder Anfrage den
Seelenzustand mit. So bleibt die Seele unabhängig von Pollens Code.

## 2026-10-08 – Eigeninitiative über `conversation.say`
Im App-Code geprüft: Der Leerlauf nach 180 s ist lokal und zufällig, ohne Sprachmodell.
Die offizielle Methode `conversation.say` auf `/rpc` lässt Reachy sofort sprechen,
und die Äußerung läuft durch Sprachkette und Vermittler. Pollens Leerlauf bleibt als Grundrauschen.

## 2026-10-08 – Haltung: Issue, dann Werkzeug, nie Fork
Eine dauerhafte Körperhaltung braucht Zugriff auf die Bewegungssteuerung der App.
Reihenfolge: Issue bei Pollen mit der Bitte um einen Haken für die Atem-Haltung;
sonst ein eigenes Werkzeug im App-Prozess; nie Pollens Dateien ändern.
Pollens Beitragsregeln verlangen bei Code-Beiträgen, dass der Autor ihn selbst versteht und
Rückfragen in eigenen Worten beantwortet. Deshalb nur ein Issue, kein Pull Request.

## 2026-10-08 – Psychologie: kleiner Kreislauf statt Modul-Zoo
Details in `docs/KONZEPT.md`. Kernpunkte: Valenz und Erregung gespeichert, Dominanz nur für die
Haltung berechnet; Bedürfnisse Nähe, Kompetenz, Gewissheit, Anregung; Selbstbild in vier
Bereichen; das Sprachmodell deutet, die Seele bewertet. Oberste Designregel: Neues nur,
wenn ein beobachtetes Verhalten ohne es fehlt.

## 2026-10-08 – Plattform: Linux zuerst, Windows zweite Priorität
Der PC läuft mit Linux. Code bleibt plattformneutral (`pathlib`, keine Shell-Spezialitäten),
damit Windows später möglich ist. Windows wird nicht aktiv getestet, bis es gebraucht wird.

## 2026-10-08 – A2: Vermittler als Proxy geht, mit Einschränkung
**Ergebnis: geht mit Einschränkung.** Ein kleiner HTTP-Proxy zwischen speech-to-speech und
llama.cpp reicht Anfragen samt Tools byte-genau durch, hängt einen Bericht an und entfernt
Tools, ohne dass Streaming oder Tool-Aufrufe brechen. Einschränkung: Geprüft nur gegen eine
Attrappe von llama.cpp, nicht gegen das echte Modell.

Geprüft an speech-to-speech Commit `8024ccf` (8. Oktober 2026, `openai==2.28.0`), Backend `responses-api`:
- Im Code gesehen: `POST <responses_api_base_url>/responses`. In `input` steht zuerst der Systemtext
  (ein englischer Rahmen von speech-to-speech um die Anweisungen der App), dann der Verlauf, zuletzt
  der neue Nutzersatz. `tools` kommen unverändert aus der Realtime-Sitzung der App,
  dazu `stream: true` und `reasoning: {"effort": "none"}`.
- Im Test bestätigt, mit dem echten Handler von speech-to-speech: Durchreichen byte-genau, Bericht
  in beiden Varianten, Tools entfernen, Streaming im Takt der Attrappe, Abbruch mitten im Strom.
  Code und Protokoll auf Branch `test/vermittler` (`docs/A2-protokoll.md`), nicht gemergt.

In A1 am echten PC nachprüfen:
1. Versteht llama.cpp `/v1/responses` mit Tools und Streaming? Sieht der Ereignisstrom so aus wie in der Attrappe?
2. Bericht als **letzter Eintrag** (Systemnachricht hinter dem Nutzersatz): Lehnt die Gesprächsvorlage
   des Modells eine Systemnachricht an dieser Stelle ab? Manche Vorlagen erlauben System nur vorne.
   Das ist die einzige Variante, deren Annahme durch llama.cpp unsicher ist.
3. Bericht **an der letzten Nutzer-Nachricht**: Das Format passt immer. Prüfen, ob das Modell den
   Bericht für Gesagtes der Person hält und darauf antwortet.
   Welche Variante das Verhalten besser steuert, klärt A3.
4. Nutzt llama.cpp den unveränderten Anfang weiter aus dem Zwischenspeicher?
5. Kommt llama.cpp klar, wenn ein Tool fehlt, das im Verlauf noch aufgerufen wurde?
6. Bricht llama.cpp die Erzeugung ab, wenn der Proxy die Verbindung schließt?

Hinweise für Phase 1:
- **Vorgreifende Anfragen:** speech-to-speech startet manchmal eine Anfrage, bevor die Person fertig
  ist, und verwirft sie wieder. Derselbe Satz kann also mehrfach durch den Vermittler laufen.
  Der Vermittler darf Gesagtes nur einmal an die Seele melden (Kreislauf-Regel 1).
  Wie er das erkennt, ist offen.
- Der Testproxy hängt den Bericht auch an die Aufwärm-Anfrage. Aufwärm- und Zusammenfassungs-Anfragen
  brauchen keinen Bericht.

## 2026-10-08 – Arbeitsweise: ein fester Arbeitsbranch, `main` nur für freigegebene Stände
Gearbeitet wird immer auf `entwicklung`, nicht mehr in einem Branch pro Aufgabe.
`main` bekommt nur Stände, die Patrick ausdrücklich freigibt („Stand sichern“, Ende einer Phase);
dann mergt Claude `entwicklung` selbst nach `main`. Sicherheitsnetz sind die Tests: Gepusht wird
nur mit grünem `pytest` und `ruff`. Patrick macht auf GitHub keine Handarbeit mehr, Claude pusht
und mergt selbst. Machbarkeitstests bleiben in eigenen `test/...`-Branches und werden nie gemergt.
Grund: Bei mehreren Branches und PRs pro Aufgabe ging der Überblick verloren (PR #2 zeigte auf
den falschen Branch), und jeder Schritt brauchte Klicks von Patrick.

## 2026-10-08 – Kein Akku, Motorschutz über das Daemon-Log
Quelle: im SDK-Code geprüft (pollen-robotics/reachy_mini, Commit `fbdbca3`: `daemon/backend/robot/backend.py` `read_hardware_errors`,
`daemon/app/routers/logs.py`, `docs/source/troubleshooting.md`). Am Roboter noch nicht geprüft, das macht A4.
Der Akkustand ist nicht lesbar (Pollen: „known limitation of the design“, nur LED). Deshalb fallen
alle Akku-Bezüge weg. Müdigkeit kommt später aus der Tageszeit, „Kannst du mich laden?“ wird zu
„Hilfst du mir kurz?“. Motorschutz: Der Daemon prüft jede Sekunde das Fehlerregister der Motoren
(Überhitzung, Überlast) und schreibt Fehler nur ins Log (`ws://<reachy>:8000/api/logs/ws/daemon`).
Ab Phase 4 liest `sinne/koerper.py` dieses Log und meldet eine Wahrnehmung; die harte Grenze ist
genau dieser Fehler. Die Motortemperatur liest der Daemon nicht, selbst auslesen hieße ihn zu
ändern, also verboten. Lesbar ist zusätzlich die IMU-Temperatur über `/api/state`.
Ein Issue bei Pollen steht im Backlog.

## 2026-10-08 – Kern von Phase 1 vorgezogen, obwohl Phase 0 offen ist
Gebaut ohne Hardware: Projektgrundlage (uv, ruff, pytest), Charakterdatei mit Lader, Grundzustand,
Zustandsbericht als Lesesicht, Erklär-Log im Speicher. Begründung: Diese Teile hängen nicht an den
offenen Punkten aus A1 (llama.cpp, Bericht-Variante) und A3 (folgt das Modell dem Bericht?).
Der Bericht ist reiner Text; wo er in der Anfrage steht, entscheidet erst der Vermittler.
Festgelegt: Erregung heißt ruhig bis aufgedreht, nicht wach bis müde. Der Bericht in Phase 1 nennt
Laune, Erregung, Art aus dem Charakter und „Halte dich kurz“. Die Erregung in Ruhe (0,3) ist ein
fester Wert im Code, kein Charakterwert. Charakterwerte: Grundstimmung 0,65, Reaktivität 0,5,
Rückkehrstärke 0,6, Geselligkeit 0,7, Neugier 0,7, Vorsicht 0,5, Ausdauer 0,6.

## Versionen (festgenagelt)
Werden in Phase 0 eingetragen (A1 und A4):

| Komponente | Version | Datum |
| --- | --- | --- |
| Reachy-Daemon / SDK | offen | |
| Conversation App | offen | |
| speech-to-speech | Commit `8024ccf` (in A2 geprüft, A1 bestätigt oder ersetzt) | 2026-10-08 |
| llama.cpp | offen | |
| Sprachmodell | offen | |
| Spracherkennung | offen | |
| Sprachausgabe | offen | |
