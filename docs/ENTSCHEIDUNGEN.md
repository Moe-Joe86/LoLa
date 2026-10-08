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
Nachtrag 8. Oktober 2026: Die Motortemperatur ist doch erreichbar, ohne den Daemon zu ändern. Der offizielle
Endpunkt `/api/move/ws/raw/write` reicht ein Lese-Paket für Register 146 an den Motor durch. Ob das bei
laufender App sauber klappt, prüft A4. Details in `ARCHITEKTUR.md`, Körperwahrnehmung.

## 2026-10-08 – Kern von Phase 1 vorgezogen, obwohl Phase 0 offen ist
Gebaut ohne Hardware: Projektgrundlage (uv, ruff, pytest), Charakterdatei mit Lader, Grundzustand,
Zustandsbericht als Lesesicht, Erklär-Log im Speicher. Begründung: Diese Teile hängen nicht an den
offenen Punkten aus A1 (llama.cpp, Bericht-Variante) und A3 (folgt das Modell dem Bericht?).
Der Bericht ist reiner Text; wo er in der Anfrage steht, entscheidet erst der Vermittler.
Festgelegt: Erregung heißt ruhig bis aufgedreht, nicht wach bis müde. Der Bericht in Phase 1 nennt
Laune, Erregung, Art aus dem Charakter und „Halte dich kurz“. Die Erregung in Ruhe (0,3) ist ein
fester Wert im Code, kein Charakterwert. Charakterwerte: Grundstimmung 0,65, Reaktivität 0,5,
Rückkehrstärke 0,6, Geselligkeit 0,7, Neugier 0,7, Vorsicht 0,5, Ausdauer 0,6.

## 2026-10-08 – A1: Sprachmodell zum Start ist Qwen3-8B, Qwen3.5 und Gemma 4 erst in A5
A1 misst die Kette und die A2-Nachprüfungen mit einem bewährten Modell: Qwen3-8B Instruct, GGUF Q4_K_M
(5,03 GB, `Qwen/Qwen3-8B-GGUF`, Apache 2.0). Die endgültige Wahl trifft A5. Kandidaten dort:
Qwen3.5-9B (Q4_K_M 5,68 GB) und Gemma 4 12B (Q4_K_M 7,12 GB).
Grafikspeicher (gemessen, Wert des Prozesses laut `nvidia-smi --query-compute-apps`): 6.010 MiB bei
Kontextlänge 8.192 Token, einem Slot (`-c 8192 --parallel 1 -ngl 999`). Mehr Kontext oder ein zweiter
Slot für den Deutungs-Aufruf kosten zusätzlich; das ist noch nicht gemessen.

Qwen3.5 und der Zwischenspeicher (gelesen, nicht gemessen):
- Qwen3.5-9B ist hybrid. Laut `config.json` und Modellkarte: 32 Schichten, 8 × (3 × Gated DeltaNet,
  dann 1 × volle Attention), also 24 Schichten mit linearer Attention.
- llama.cpp `d812350` unterstützt das Modell (`src/models/qwen35.cpp`) und führt dafür einen hybriden
  Speicher (`llama-memory-hybrid`, `llama-memory-recurrent`).
- Folge: Der Zustand der DeltaNet-Schichten lässt sich nicht an beliebiger Stelle abschneiden
  (`llama_memory_recurrent::seq_rm`). Zurückrollen geht nur um wenige Token (`n_rs_seq`, als
  experimentell markiert) oder auf einen gespeicherten Kontext-Checkpoint (`--ctx-checkpoints`,
  Standard 32 pro Slot, Mindestabstand 8192 Token).
- Für uns heißt das: Reines Anhängen am Ende nutzt den Zwischenspeicher. Unser Bericht steht aber am
  Ende und ändert sich bei jeder Anfrage, die nächste Anfrage weicht also mitten im alten Text ab.
  Vermutung: Ohne passenden Checkpoint rechnet llama.cpp dann den ganzen Anfang neu. A5 muss das
  mit Qwen3.5 messen, bevor es gewählt wird. Qwen3-8B hat nur volle Attention und das Problem nicht.

„Nicht nachdenken“ kommt an (gemessen, llama.cpp `d812350`, `/v1/responses`, Streaming, `--jinja`):

| Anfrage | Denk-Ereignisse | `<think>` im Text | Ausgabe-Token |
| --- | --- | --- | --- |
| ohne Angabe | 218 (`response.reasoning_text.delta`) | nein | 281 |
| `reasoning: {"effort": "none"}` (so sendet speech-to-speech) | 0 | nein | 93 |
| `chat_template_kwargs: {"enable_thinking": false}` | 0 | nein | 139 |

Auch ohne Abschalten landet das Nachdenken nicht im Antworttext, sondern in eigenen Ereignissen.
Es kostet aber Zeit bis zum ersten Wort. Eine Frage, ein Lauf je Zeile.

## 2026-10-08 – A1: Hardware des PCs
Linux (Pop!_OS 24.04), Intel i9-9900K (8 Kerne, 16 Threads, AVX2, kein AVX-512), 32 GB DDR4-3600,
NVIDIA RTX 3080 Ti mit 12 GB, Treiber 580.119.02, CUDA-Werkzeuge 12.0. Der Desktop belegt im Leerlauf
rund 0,6 GB Grafikspeicher. Das Sprachmodell läuft vollständig im Grafikspeicher (`-ngl 999`).
Die Laufzeit (llama.cpp, speech-to-speech, Modelle) liegt außerhalb des Repos in `~/lola-laufzeit/`.

## 2026-10-08 – A1, Zwischenstand: Sprachausgabe Qwen3-TTS (GGML)
Gemessen mit faster-qwen3-tts 0.5.4 und qwentts-cpp-python 0.5.0, Sprache Deutsch, je 5 Sätze.
Grafikspeicher ist der Wert des Prozesses (`nvidia-smi --query-compute-apps`); Gesamtbelegung vor dem
Start 639 MiB.

| Variante | Grafikspeicher im Betrieb | erster Ton | Rechenzeit je Sekunde Sprache |
| --- | --- | --- | --- |
| 0.6B CustomVoice Q8_0 | 2.512 MiB | 0,07 s | 0,10 s |
| 1.7B CustomVoice Q4_K_M | 2.694 MiB | 0,07 s | 0,11 s |
| 1.7B CustomVoice Q8_0 | 3.536 MiB | 0,08 s | 0,12 s |
| 0.6B Base Q8_0 mit Referenzstimme | 2.968 bis 3.010 MiB | 0,08 s | 0,11 s |
| 1.7B Base Q4_K_M mit Referenzstimme | 3.150 bis 3.194 MiB | 0,08 s | 0,11 s |
| 1.7B Base Q8_0 mit Referenzstimme | 4.004 bis 4.046 MiB | 0,09 s | 0,13 s |
| 0.6B CustomVoice Q8_0 auf der CPU, 8 Threads | 0 | 0,88 s | 1,45 s |

- Das GGML-Backend lädt 0.6B, als CustomVoice und als Base.
- Keine Variante hält die geplante Grenze von 2 GB. Vom Speicher der kleinsten Variante sind rund
  1,16 GB Gewichte und 896 MB ein fest reservierter Zwischenspeicher (`max_seq_len 4096`), den die
  Python-Anbindung nicht einstellbar macht. Puffer des Tonwandlers und Flash Attention ändern nichts.
- `parity_mode` wirkt im GGML-Backend nicht; CUDA-Graphen gibt es nur im Torch-Backend.
- Auf der CPU ist die Sprachausgabe zu langsam (Ziel: erster Ton unter 0,3 s, Rechenzeit unter 0,5 s).
- Entscheidung: Für A1 gilt eine Grenze von 3 GB, A5 bewertet neu. Die Wahl der Variante hängt an
  Patricks Urteil zum Klang und ist offen.
- Verständlichkeit: Alle 61 Testdateien von faster-whisper large-v3-turbo zurückgelesen, fast alles
  wortgleich. Ausrutscher in je einem Lauf bei 1.7B Q4_K_M: Stimme „ryan“ brach nach dem ersten Satz ab,
  „serena“ sprach „Timmer“, „sohee“ „Nullen“ statt „Nudeln“.

## 2026-10-08 – A1: Antworten auf die sechs Nachprüfungen aus A2
Gemessen mit dem Proxy aus `test/vermittler` gegen llama.cpp `d812350` mit Qwen3-8B Q4_K_M, Anfrage vom
echten Handler aus speech-to-speech `8024ccf` (680 Eingabe-Token mit vier Tools). Zwei Läufe.
Protokoll auf Branch `test/a1` (`docs/A1-protokoll.md`).

1. **`/v1/responses` mit Tools und Streaming: ja.** Der echte Handler verarbeitet Text und Tool-Aufruf,
   direkt und über den Proxy. Der Ereignisstrom enthält mehr Typen als die Attrappe:
   `response.in_progress`, `response.function_call_arguments.delta`, `response.content_part.added/done`
   und, wenn das Nachdenken an ist, `response.reasoning_text.delta`. Bei einem Tool-Aufruf kam kein Text davor.
2. **Bericht als letzter Eintrag: wird angenommen** (HTTP 200). Die Vorlage von Qwen3 setzt die
   Systemnachricht als eigenen Block hinter den Nutzersatz. Gilt nur für diese Vorlage, bei einem
   anderen Modell neu prüfen.
3. **Bericht an der Nutzer-Nachricht: wird angenommen.** In 10 Antworten hielt das Modell den Bericht
   nie für Gesagtes der Person. Bei der Variante „letzter Eintrag“ schrieb es den Zustand einmal der
   Person zu („Du bist müde? Dann ruh dich aus.“). Kleine Stichprobe, die Wahl trifft A3.
4. **Zwischenspeicher: ja.** In der zweiten Runde kamen ohne Bericht 676 von 700 Eingabe-Token aus dem
   Zwischenspeicher, mit Bericht als Eintrag 674 von 725, mit Bericht an der Nutzer-Nachricht 670 von 725.
   Neu gerechnet wird nur ab der Stelle des alten Berichts. Erster Text nach 0,03 bis 0,04 s.
5. **Fehlendes Tool: llama.cpp kommt klar** (HTTP 200, kein Fehler), obwohl `move_head` im Verlauf
   aufgerufen wurde und nicht mehr angeboten wird.
6. **Abbruch: ja.** Nach dem Schließen der Verbindung arbeitete llama.cpp höchstens 0,05 s weiter
   (Messauflösung), direkt und über den Proxy. Gegenprobe ohne Abbruch: 23,3 s für 3.000 Token.
   Die nächste Anfrage über denselben Proxy lief normal.

Nebenbefunde für A3, je wenige Läufe:
- Ohne Bericht rief das Modell bei „Kannst du für mich tanzen?“ immer das Tool `dance` auf. Mit Bericht
  („müde und eher zurückhaltend“) antwortete es in 3 von 4 Fällen stattdessen englisch mit
  „Sure, here's my best dance.“, ohne Tool. Der Satz stammt aus dem englischen Rahmentext von
  speech-to-speech. Ob der Bericht die Tool-Aufrufe stört oder das Modell wegen „müde“ nicht tanzt, ist offen.
- Auf „Wie spät ist es?“ erfand das Modell eine Uhrzeit. Ein Uhrzeit-Tool fehlte im Test.

## Versionen (festgenagelt)
Werden in Phase 0 eingetragen (A1 und A4):

| Komponente | Version | Datum |
| --- | --- | --- |
| Reachy-Daemon / SDK | offen | |
| Conversation App | offen | |
| speech-to-speech | Commit `8024ccf` (in A2 geprüft, in A1 installiert) | 2026-10-08 |
| llama.cpp | Commit `d81235049384534c167caea52b85a694f6103d14` (0.6.0), CUDA 12.0, gcc 12 | 2026-10-08 |
| Sprachmodell | Qwen3-8B Q4_K_M, `Qwen/Qwen3-8B-GGUF` Stand `7c41481`, SHA-256 `d98cdcbd…5745785` (nur für A1, Wahl in A5) | 2026-10-08 |
| Spracherkennung | offen (Messung in A1 steht aus); installiert: faster-whisper 1.2.1, ctranslate2 4.8.2, nano-parakeet 0.2.1 | |
| Sprachausgabe | Variante offen; faster-qwen3-tts 0.5.4, qwentts-cpp-python 0.5.0, GGUF aus `Serveurperso/Qwen3-TTS-GGUF` | 2026-10-08 |
| PyTorch | 2.14.1+cu130 | 2026-10-08 |
