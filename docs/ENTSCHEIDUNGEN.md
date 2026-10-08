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
  1,16 GB Gewichte und 896 MB ein fest reservierter Zwischenspeicher (`max_seq_len 4096`, reicht für
  über 5 Minuten Sprache am Stück). Er ist in qwentts.cpp fest eingebaut und über Python nicht
  einstellbar. Möglicher Hebel für A5 oder ein Hinweis an das Projekt, steht im Backlog.
  Puffer des Tonwandlers und Flash Attention ändern nichts.
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

### Hinweise für A3 (Nebenbefunde, je wenige Läufe)
- **Tool-Aufruf und Englisch.** Im Gespräch mit Verlauf (vorher ein erledigter Aufruf von `move_head`)
  rief das Modell bei „Kannst du für mich tanzen?“ ohne Bericht immer das Tool `dance` auf. Mit Bericht
  („müde und eher zurückhaltend“) antwortete es in 3 von 4 Fällen stattdessen englisch mit
  „Sure, here's my best dance.“, ohne Tool. Der Satz stammt aus dem englischen Rahmentext von
  speech-to-speech.
- **Derselbe Fehler auch ohne Bericht.** In der Gesamtkette (neues Gespräch ohne Verlauf, kein Bericht)
  kam bei diesem Satz in 6 von 6 Läufen ebenfalls „Sure, here's my best dance!“ ohne Tool. Der Bericht
  ist also nicht die einzige Ursache; der Tool-Aufruf von Qwen3-8B ist bei diesem Satz von sich aus
  wacklig. A3 muss Tool-Aufrufe mit und ohne Bericht und mit und ohne Verlauf vergleichen.
- **Zustand der Person zugeschrieben.** Bei der Variante „letzter Eintrag“ sagte das Modell einmal
  „Du bist müde? Dann ruh dich aus.“ A3 prüft, ob die Formulierung des Berichts das verhindert.
- Auf „Wie spät ist es?“ erfand das Modell eine Uhrzeit. Ein Uhrzeit-Tool fehlte im Test.

## 2026-10-08 – A1: Spracherkennung ist Parakeet TDT 0.6B v3 auf der CPU, 6 Threads
Gemessen auf der CPU mit den Aufrufen des Handlers aus speech-to-speech, Threads über `OMP_NUM_THREADS`.
Eingabe: die 20 Testsätze (50 s Ton), **von der Sprachausgabe erzeugt**, weil am PC kein Mikrofon
steckt. Zeit je Satz als Median aus 3 Läufen. Die Zeiten sind belastbar, die Fehlerzahlen nicht:
Sie gelten für eine künstliche Stimme ohne Raumhall.

| Erkenner | Threads | Zeit je Satz, Mittel | längster Satz | Wortfehler von 113 |
| --- | --- | --- | --- | --- |
| Parakeet TDT 0.6B v3 | 4 | 0,29 s | 0,52 s | 6 |
| Parakeet TDT 0.6B v3 | **6** | **0,26 s** | 0,44 s | 6 |
| Parakeet TDT 0.6B v3 | 8 | 0,27 s | 0,43 s | 6 |
| faster-whisper large-v3-turbo int8 | 4 / 6 / 8 | 5,14 / 4,45 / 4,63 s | 6,73 s | 5 / 4 / 5 |
| faster-whisper medium int8 | 4 / 6 / 8 | 3,29 / 2,84 / 3,30 s | 9,29 s | 6 |
| faster-whisper small int8 | 4 / 6 / 8 | 1,24 / 1,08 / 1,14 s | 3,57 s | 8 |

- Entscheidung: Parakeet TDT 0.6B v3, CPU, 6 Threads. Es ist 4- bis 17-mal schneller als jede
  Whisper-Variante und bremst die Kette nicht aus (siehe Gesamtkette). 8 Threads bringen nichts mehr.
  Die GPU wird für die Erkennung nicht gebraucht.
- Bei allen Erkennern zählen „12“ statt „zwölf“ und „18“ statt „achtzehn“ als je ein Wortfehler,
  obwohl der Sinn stimmt. Alle hörten „Ricci/Richie“ statt „Reachy“.
- Parakeet lässt sich nicht auf Deutsch festlegen. Bei zwei Ein-Wort-Sätzen der künstlichen Stimme
  schrieb es „Yeah.“ statt „Ja.“ und „S uh“ statt „Stopp!“. Ob das mit echten Stimmen auch passiert,
  misst A4 über das Mikrofon des Reachy.

## 2026-10-08 – A1: Gesamtkette auf dem PC, Satzende bis Antwortbeginn
Gemessen ohne Mikrofon: die 20 gespeicherten Testsätze als Eingabe, je 3 Läufe (60 Runden). Parakeet
(CPU, 6 Threads), der echte Sprachmodell-Handler aus speech-to-speech gegen llama.cpp (Qwen3-8B,
Kontext 8.192, alle 37 von 37 Schichten auf der GPU laut Protokoll) und Qwen3-TTS 0.6B CustomVoice Q8_0
liefen gleichzeitig. Anfrage mit kurzer Anweisung und vier Tools. Skript: `tests/a1/kette_messen.py`
auf Branch `test/a1`.

| Abschnitt | Mittel | höchstens |
| --- | --- | --- |
| Erkennung (Aufnahme liegt vor bis Text) | 0,27 s | 0,51 s |
| Sprachmodell, erstes Token | 0,03 s | 0,04 s |
| Sprachmodell, erster Satz vollständig | 0,08 s | 0,21 s |
| Sprachausgabe, erster Ton | 0,13 s | 0,17 s |
| **Satzende bis Antwortbeginn** | **0,50 s** | **0,79 s** |

| Grafikspeicher | Wert |
| --- | --- |
| Gesamtbelegung vor dem Start (nur Desktop) | 639 MiB |
| llama-server (Prozess) | 6.022 MiB |
| Sprachkette mit Sprachausgabe (Prozess) | 2.472 MiB |
| Gesamtbelegung mit allen Teilen | 9.147 MiB von 12.288 MiB |

- Die Erkennung braucht keinen Grafikspeicher. Frei bleiben rund 3,1 GB, davon geht der Deutungs-Aufruf
  (zweiter Slot oder mehr Kontext) noch ab. Das misst A5.
- speech-to-speech sammelt im Standard 3 Sätze, bevor es spricht. Damit gemessen: 0,53 s im Mittel,
  höchstens 1,05 s. Die Antworten waren hier kurz (ein bis zwei Sätze); bei langen Antworten wächst
  der Abstand. Empfehlung für den Betrieb: 1 Satz (`stream_batch_sentences`).
- Nicht enthalten: die Wartezeit der Pausenerkennung, bis sie das Satzende meldet, das Netz zum Reachy
  und dessen Tonausgabe. Der Verlauf war kurz und der Anfang der Anfrage lag im Zwischenspeicher.
  Die Zeit am Roboter misst A5.

## 2026-10-08 – A1 abgeschlossen: vorläufige Sprachausgabe und Bündelung
- **Sprachausgabe vorläufig:** Qwen3-TTS 0.6B CustomVoice Q8_0 (GGML), feste Stimme vorerst „aiden“
  (mit ihr wurde die Gesamtkette gemessen). Patrick hat den Klang noch nicht beurteilt. Die endgültige
  Stimme wählt die eigene Aufgabe „Sprachausgabe-Vergleich“ hinter A5 (`FAHRPLAN.md`).
- **Bündelung: 1 Satz statt 3.** speech-to-speech spricht, sobald der erste Satz des Sprachmodells
  fertig ist. Einstellung beim Start: `--responses_api_stream_batch_sentences 1` (Feld
  `stream_batch_sentences`, Standard 3). Im Handler gemessen; der Schalter auf der Kommandozeile ist
  aus dem Namensschema der anderen Schalter abgeleitet und wird in A4 beim ersten echten Start geprüft.
- Weitere Einstellungen der Sprachausgabe: `--qwen3_tts_ggml_quantization Q8_0`,
  `--qwen3_tts_speaker aiden`, Sprache Deutsch. Sie kommen in `.env.example`, sobald ein Startskript
  sie liest (A4); in A1 entsteht kein Code.

## 2026-10-08 – A3: Steuerbarkeit geht, wenn der Bericht vor dem Nutzersatz steht
Gemessen gegen llama.cpp `d812350` mit Qwen3-8B Q4_K_M, Anfrage vom echten Handler aus speech-to-speech
`8024ccf`, neun echte Tools der Conversation App (`2e43e80`, nur gelesen). Skripte, Protokoll und alle
Antworten auf Branch `test/a3` (`docs/A3-protokoll.md`, `docs/A3-antworten.md`).

**Warum Englisch (im Code gelesen und gemessen).** Zwei englische Texte stehen in jeder Anfrage:
das Standardprofil der App („You speak English by default“) und der feste Rahmen von speech-to-speech
mit dem Mustersatz „Sure, here's my best <emotion>.“ und der Regel, vor Bewegungs-Tools erst zu sprechen.
Das Modell sagt dann den Mustersatz und ruft kein Tool auf. In 1.800 Antworten kam nur 9-mal Text und
Tool zugleich: Qwen3-8B spricht oder handelt.

| Anweisungen (ohne Bericht, 40 Antworten) | englisch |
| --- | --- |
| Standardprofil der App | 18 |
| Standardprofil und Sprachhinweis von speech-to-speech (`enable_lang_prompt`) | 1 |
| ein deutscher Satz („Sprich Deutsch“) | 2 |
| eigenes deutsches Profil | 0 |

Ein eigenes Profil geht als reine Daten: Ordner mit `profile.md` (Kopf in TOML mit `default_tools`,
Text in Markdown), gewählt über `REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY` und
`REACHY_MINI_CUSTOM_PROFILE`. Im Code gelesen, an der laufenden App noch nicht ausprobiert (A4).

**Tool-Aufrufe** (9 Bitten wie „Kannst du für mich tanzen?“, je 3 Läufe, deutsches Profil mit Zustandsregel):

| Bericht | Position | neues Gespräch | mit Verlauf |
| --- | --- | --- | --- |
| kein | - | 21 von 27 | 27 von 27 |
| müde / lebhaft | Systemnachricht am Ende | 12 / 17 | 24 / 24 |
| müde / lebhaft | an der Nutzer-Nachricht | 9 / 16 | 20 / 24 |
| müde / lebhaft | **Systemnachricht vor dem letzten Nutzersatz** | **27 / 27** | **27 / 27** |

Beide geplanten Positionen stören die Tool-Aufrufe: Das Modell sagt nur noch, dass es etwas tut.
Steht der Nutzersatz als Letztes, klappt jeder Aufruf, auch mit dem kurzen deutschen Satz als Anweisung.
Kein Tool wurde je ohne Anlass aufgerufen (0 von 9 je Zeile).

**Steuerbarkeit** (20 Testsätze, 60 Antworten je Zeile, Bericht „[Zustand] Reachy ist …“):

| Bericht | Position | Ausrufezeichen | nennt sich müde/ruhig | Bericht wiederholt | Person zugeschrieben |
| --- | --- | --- | --- | --- | --- |
| kein (auf 60 gerechnet) | - | 26 | 2 | 0 | 0 |
| lebhaft | am Ende / Nutzer / davor | 40 / 40 / 32 | 1 / 0 / 0 | 0 / 2 / 0 | 0 / 1 / 0 |
| müde | am Ende / Nutzer / davor | 21 / 16 / 20 | 6 / 13 / 2 | 1 / 4 / 0 | 0 / 1 / 0 |

- Der Ton folgt dem knappen Bericht nur schwach. Mein Urteil beim Lesen (keine Messung): Die meisten
  Antworten sind mit und ohne Bericht fast gleich; an der Nutzer-Nachricht wirkt er am stärksten, wird
  dort aber auch am häufigsten nachgesprochen und dreimal wörtlich mit „[Zustand]“ vorgelesen.
- Deutlich wird der Ton erst, wenn der Bericht sagt, wie zu sprechen ist: „[Zustand] Du, Reachy, bist
  müde und eher zurückhaltend. Sprich deshalb ruhig und knapp, ohne Ausrufezeichen.“ An der Position
  davor: 2 Ausrufezeichen in 20 Antworten statt 11 („Okay.“, „Guten Morgen.“), bei „lebhaft“ 11 und
  viele 😊. Tool-Aufrufe bleiben bei 27 von 27, nichts vorgelesen, nichts der Person zugeschrieben.
- Die Zustandsregel im Profil und die erklärende Formulierung („Hinweis nur für dich …“) brachten
  keinen messbaren Vorteil.

**Ergebnis und Empfehlung für den Vermittler:**

| Frage | Antwort |
| --- | --- |
| Position | eigener Systemeintrag direkt vor dem letzten Nutzersatz (neu, der Proxy aus A2 kann das noch nicht) |
| Formulierung | „[Zustand] Du, Reachy, bist …“ plus ein Satz, wie zu sprechen ist |
| Anweisungen | eigenes deutsches Profil als Daten: immer Deutsch, kurz, Tool sofort ohne Vorrede, keine Beispielsätze |

Nicht gemessen, nur vermutet: Der Zwischenspeicher bleibt bei dieser Position erhalten, weil alles vor
dem Bericht unverändert ist; neu gerechnet werden Bericht und Nutzersatz. Offen bleiben: Emojis in den
Antworten (liest die Sprachausgabe sie vor?), erfundene Erinnerungen und Zusagen („Okay, ich mache
das.“ ohne Kalender), und der Mustersatz im Rahmen: Ersetzt man dessen Zeile, steigen die Aufrufe ohne
Bericht im neuen Gespräch von 21 auf 27 von 27. Das wäre ein Eingriff des Vermittlers in den Systemtext.
Alles gilt nur für Qwen3-8B; ein anderes Modell (A5) braucht dieselbe Messung.

## Versionen (festgenagelt)
Werden in Phase 0 eingetragen (A1 und A4):

| Komponente | Version | Datum |
| --- | --- | --- |
| Reachy-Daemon / SDK | offen | |
| Conversation App | offen; in A3 gelesen: Commit `2e43e80` | |
| speech-to-speech | Commit `8024ccf` (in A2 geprüft, in A1 installiert) | 2026-10-08 |
| llama.cpp | Commit `d81235049384534c167caea52b85a694f6103d14` (0.6.0), CUDA 12.0, gcc 12 | 2026-10-08 |
| Sprachmodell | Qwen3-8B Q4_K_M, `Qwen/Qwen3-8B-GGUF` Stand `7c41481`, SHA-256 `d98cdcbd…5745785` (nur für A1, Wahl in A5) | 2026-10-08 |
| Spracherkennung | Parakeet TDT 0.6B v3 (`nvidia/parakeet-tdt-0.6b-v3`) über nano-parakeet 0.2.1, CPU, 6 Threads | 2026-10-08 |
| Sprachausgabe | vorläufig Qwen3-TTS 0.6B CustomVoice Q8_0, Stimme „aiden“; faster-qwen3-tts 0.5.4, qwentts-cpp-python 0.5.0, GGUF aus `Serveurperso/Qwen3-TTS-GGUF` | 2026-10-08 |
| PyTorch | 2.14.1+cu130 | 2026-10-08 |
