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

## Versionen (festgenagelt)
Werden in Phase 0 eingetragen (A1 und A4):

| Komponente | Version | Datum |
| --- | --- | --- |
| Reachy-Daemon / SDK | offen | |
| Conversation App | offen | |
| speech-to-speech | offen | |
| llama.cpp | offen | |
| Sprachmodell | offen | |
| Spracherkennung | offen | |
| Sprachausgabe | offen | |
