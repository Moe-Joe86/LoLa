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
(Überhitzung, Überlast) und schreibt Fehler nur ins Log (`ws://<reachy>:8000/logs/ws/daemon`).
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
Mit `reasoning: {"effort": "none"}`, so wie speech-to-speech sendet, kamen 0 Denk-Ereignisse statt 218.
Auch ohne Abschalten landet das Nachdenken nicht im Antworttext, sondern in eigenen Ereignissen.
Es kostet aber Zeit bis zum ersten Wort. Eine Frage, ein Lauf je Zeile, Tabelle in `MESSUNGEN.md`.

## 2026-10-08 – A1: Hardware des PCs
Linux (Pop!_OS 24.04), Intel i9-9900K (8 Kerne, 16 Threads, AVX2, kein AVX-512), 32 GB DDR4-3600,
NVIDIA RTX 3080 Ti mit 12 GB, Treiber 580.119.02, CUDA-Werkzeuge 12.0. Der Desktop belegt im Leerlauf
rund 0,6 GB Grafikspeicher. Das Sprachmodell läuft vollständig im Grafikspeicher (`-ngl 999`).
Die Laufzeit (llama.cpp, speech-to-speech, Modelle) liegt außerhalb des Repos in `~/lola-laufzeit/`.

## 2026-10-08 – A1, Zwischenstand: Sprachausgabe Qwen3-TTS (GGML)
Gemessen mit faster-qwen3-tts 0.5.4 und qwentts-cpp-python 0.5.0, Sprache Deutsch, je 5 Sätze.
Grafikspeicher ist der Wert des Prozesses (`nvidia-smi --query-compute-apps`); Gesamtbelegung vor dem
Start 639 MiB.

Ergebnis: Auf der GPU brauchen die Varianten 2,5 bis 4,0 GB, der erste Ton kommt nach 0,07 bis
0,09 s. Die kleinste ist 0.6B CustomVoice Q8_0 mit 2.512 MiB. Tabelle in `MESSUNGEN.md`.

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

Ergebnis: Parakeet braucht 0,26 s je Satz (6 Threads), faster-whisper je nach Größe 1,08 bis 5,14 s.
Die Wortfehler liegen bei allen zwischen 4 und 8 von 113. Tabelle in `MESSUNGEN.md`.

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

Ergebnis: 0,50 s im Mittel vom Satzende bis zum Antwortbeginn, höchstens 0,79 s. Davon Erkennung 0,27 s,
Sprachmodell bis zum ersten Satz 0,08 s, Sprachausgabe bis zum ersten Ton 0,13 s. Grafikspeicher mit
allen Teilen: 9.147 von 12.288 MiB (llama-server 6.022, Sprachkette 2.472, Desktop 639).
Tabellen in `MESSUNGEN.md`.

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
  fertig ist. Einstellung beim Start: `--stream_batch_sentences 1` (Standard 3). Im Handler
  gemessen; der Schalter ist in A4 an `--help` und beim Start geprüft (die frühere Annahme
  `--responses_api_stream_batch_sentences` war falsch).
- Weitere Einstellungen der Sprachausgabe: `--qwen3_tts_ggml_quantization Q8_0`,
  `--qwen3_tts_speaker aiden`, Sprache Deutsch. Sie kommen in `.env.example`, sobald ein Startskript
  sie liest (A4); in A1 entsteht kein Code.

## 2026-10-08 – A3: Steuerbarkeit geht, wenn der Bericht vor dem Nutzersatz steht
Gemessen gegen llama.cpp `d812350` mit Qwen3-8B Q4_K_M, Anfrage vom echten Handler aus speech-to-speech
`8024ccf`, neun echte Tools der Conversation App (`2e43e80`, nur gelesen). Tabellen in `MESSUNGEN.md`,
Skripte, Protokoll und alle Antworten auf Branch `test/a3`.

- **Warum Englisch (im Code gelesen und gemessen).** Zwei englische Texte stehen in jeder Anfrage:
  das Standardprofil der App („You speak English by default“) und der feste Rahmen von speech-to-speech
  mit dem Mustersatz „Sure, here's my best <emotion>.“ und der Regel, vor Bewegungs-Tools erst zu
  sprechen. Mit dem Standardprofil waren 18 von 40 Antworten englisch, mit einem eigenen deutschen
  Profil 0.
- **Sprechen oder handeln.** Qwen3-8B gibt fast nie Text und Tool-Aufruf zugleich (9 von 1.800).
  Sagt es den Mustersatz, ruft es kein Tool auf.
- **Profil als Daten.** Ordner mit `profile.md` (Kopf in TOML mit `default_tools`, Text in Markdown),
  gewählt über `REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY` und `REACHY_MINI_CUSTOM_PROFILE`. Im Code
  gelesen, an der laufenden App noch nicht ausprobiert (A4). Beispielsätze im Profil spricht das
  Modell nach, statt das Tool aufzurufen.
- **Position.** Am Ende der Anfrage und an der Nutzer-Nachricht stört der Bericht die Tool-Aufrufe
  (9 bis 17 von 27 im neuen Gespräch): Das Modell sagt nur noch, dass es etwas tut. Als eigener
  Systemeintrag vor dem letzten Nutzersatz klappen 27 von 27, mit und ohne Verlauf. An dieser
  Position wurde der Bericht nie vorgelesen und nie der Person zugeschrieben.
- **Formulierung.** Dem knappen Bericht („Reachy ist müde“) folgt der Ton nur schwach. Deutlich wird
  er, wenn der Bericht sagt, wie zu sprechen ist: 2 statt 11 Ausrufezeichen in 20 Antworten, die
  Tool-Aufrufe bleiben bei 27 von 27.
- **Ohne Vorteil:** eine Zustandsregel im Profil und eine erklärende Formulierung des Berichts.
- Alles gilt nur für Qwen3-8B; ein anderes Modell (A5) braucht dieselbe Messung.

## 2026-10-08 – Nach A3: Position, Sprechanweisung, Mustersatz, deutsches Profil
Patricks Entscheidungen zum Ergebnis von A3:

| Frage | Entscheidung |
| --- | --- |
| Position des Berichts | eigener Systemeintrag direkt vor dem letzten Nutzersatz, nicht mehr am Ende |
| Inhalt des Berichts | Zustand plus Sprechanweisung, beides aus derselben festen Stufentabelle |
| Rahmen von speech-to-speech | bleibt unverändert, der Mustersatz wird vorerst nicht ersetzt |
| Anweisungen | eigenes deutsches Profil als Daten (A4) |

- **Position.** Begründung: nur so klappen alle Tool-Aufrufe. Der Proxy aus A2 kann die Position noch
  nicht. Ob der Zwischenspeicher dort hält, ist nur vermutet (alles vor dem Bericht bleibt gleich,
  neu gerechnet würden Bericht und Nutzersatz). Gemessen wird es, wenn der Vermittler gebaut wird.
  Die Frage zu hybriden Modellen wie Qwen3.5 (Eintrag zu A1) bleibt dieselbe: Auch an der neuen
  Position weicht die nächste Anfrage kurz vor dem Ende vom alten Text ab.
- **Sprechanweisung.** Sie kommt aus derselben Stufentabelle in `seele/zustandsbericht.py` wie der
  Zustand: keine freien Texte, keine Beispielsätze. So bleibt der Bericht eine Lesesicht, und das
  Modell bekommt nichts zum Nachsprechen. Regel in `KONZEPT.md`, Schnittstelle zum Sprachmodell.
  Gebaut ist das noch nicht; der heutige Bericht hat eine andere Form als die gemessene.
- **Mustersatz.** Der Vermittler reicht den Systemtext weiter unverändert durch. Option, falls die
  Tool-Aufrufe am Roboter wackeln: Ersetzt man die Zeile mit dem Mustersatz, steigen die Aufrufe
  ohne Bericht im neuen Gespräch von 21 auf 27 von 27. Mit dem Bericht vor dem Nutzersatz sind es
  auch ohne diesen Eingriff 27 von 27.
- **Deutsches Profil.** Immer Deutsch, kurz, Tool sofort ohne Vorrede, keine Beispielsätze. Dazu
  wegen der Nebenbefunde aus A3: keine Emojis, keine Zusagen für Fähigkeiten, die Reachy nicht hat,
  keine erfundenen Erinnerungen. Ob das Modell sich daran hält, zeigt A4.
- **Dokumente.** Die Grenze von 300 Zeilen gilt nur für Code. Messtabellen stehen ab jetzt in
  `MESSUNGEN.md`; hier bleiben Ergebnis, Begründung und Verweis.

## 2026-10-08 – Sprachausgabe für den Betrieb: Qwen3-TTS 0.6B Base Q8_0 mit Referenzstimme „frau“
Ersetzt die vorläufige Wahl („aiden“) aus dem Abschluss von A1.

- **Klangurteil (Patrick):** Am besten klingen Base Q8_0 in 0.6B und 1.7B mit der Referenzstimme „frau“.
- **Wahl:** 0.6B Base Q8_0 (GGML) mit „frau“, als vorab berechnete Stimmdaten (`.spk` und `.rvq`).
  So entstehen sie nicht bei jedem Start neu, und die Aufnahme selbst wird im Betrieb nicht gebraucht.
- **Grafikspeicher (gemessen):** 2.624 bis 2.722 MiB für den Prozess, 5 normal lange Sätze, 3 frische
  Prozesse; nach dem Laden 2.348 MiB. Erster Ton nach 0,07 s. Die Grenze von 3 GB hält.
  Tabelle in `MESSUNGEN.md`. Mit der Aufnahme statt der Stimmdaten waren es 2.968 bis 3.010 MiB.
- **Nicht gemessen:** die Gesamtkette mit dieser Stimme. Gerechnet aus den Einzelwerten wären es rund
  9,3 bis 9,4 GB statt 9,1 GB.
- **Auffälligkeit:** Einmal in 27 Sätzen war die Ausgabe 13 s lang statt rund 4 s. Der Inhalt ist nicht
  geprüft, in 12 Wiederholungen desselben Satzes kam es nicht wieder vor. In A4 darauf achten.
- **Kein Sprachausgabe-Vergleich mehr:** Die Aufgabe A5b (F5-TTS, Fish Speech) entfällt, sie ist mit
  dieser Wahl erledigt und aus dem Fahrplan gestrichen. F5-TTS und Fish Speech wurden nicht gemessen.
- **Option für A5:** 1.7B Base Q8_0 mit derselben Stimme (rund 4 GB mit der Aufnahme gemessen), falls
  dann Speicher übrig ist. Die Stimmdaten gelten je Modell und müssten dafür neu berechnet werden
  (gelesen: der Schlüssel der Bibliothek enthält das Modell).
- **Einstellungen:** `--qwen3_tts_ref_spk`, `--qwen3_tts_ref_rvq` und `--qwen3_tts_ref_text` (der
  Wortlaut der Aufnahme). Im Code von speech-to-speech gelesen; gemessen wurde über die Bibliothek
  direkt, der Start über speech-to-speech wird in A4 geprüft.
- **Schutz der Stimme:** Eine Referenzstimme einer realen Person wird nur mit deren Zustimmung
  verwendet und bleibt lokal. Stimmprobe, Wortlaut und Stimmdaten liegen nur in
  `~/lola-laufzeit/stimmen/`, nie im Repo und nie im Netz. `.gitignore` schließt `*.spk` und `*.rvq` aus.
  Die Bibliothek legt Stimmdaten zusätzlich selbst ab, wenn sie eine Aufnahme bekommt
  (`~/.cache/faster-qwen3-tts/qwentts_refs/`, ebenfalls lokal).
- **Nur ein Ort für Stimmdaten:** speech-to-speech startet mit
  `--qwen3_tts_ref_cache_dir ~/lola-laufzeit/stimmen/`; für die Bibliothek direkt gilt die
  Umgebungsvariable `FQWEN3TTS_QWENTTS_REF_CACHE_DIR`. Im Code gelesen: Mit `.spk`/`.rvq` als
  Eingabe schreibt die Bibliothek gar keine Stimmdaten, der Ordner greift nur, falls doch einmal
  eine Aufnahme übergeben wird. Geprüft wird der Schalter beim ersten Start in A4.

## 2026-10-09 – A4: Stände am Reachy festgenagelt, Fehler in der Update-Prüfung des Daemons
- **Festgenagelt:** Daemon 1.11.0, Conversation App 1.0.1 (`ddc3096`), Reachy Control 0.9.35 auf dem PC.
- **Geprüft an der laufenden App:** alle 30 Dateien der Einstellungsseite haben dieselbe Prüfsumme wie
  im Stand `ddc3096`; `/rpc` antwortet auf `conversation.status`. Die Reachy-Bibliothek in der
  gemeinsamen App-Umgebung erfüllt `>=1.10.0rc5` (die Installation hat sie nicht getauscht); fünf
  Zeilennummern im Log passen zum Code von 1.11.0. Die genaue Version ist damit abgeleitet, nicht abgelesen.
- **Fehler im Daemon 1.11.0:** Alle Apps teilen sich eine Umgebung (`/venvs/apps_venv`).
  `apps/sources/app_update_checker.py` sucht die Paketdaten mit `{name}*.dist-info`. Für
  `reachy_mini_conversation_app` trifft das auch `reachy_mini_conversation_app_local` (fremde App).
  Folgen, beide am Roboter gesehen: Die Update-Prüfung meldet „aktuell“, obwohl 0.9.0 statt 1.0.1
  installiert war. Das Update entfernte Pollens App und installierte die fremde neu; dabei fiel die
  Reachy-Bibliothek in der Umgebung von 1.11.0 auf 1.8.0.
- **Behebung:** fremde App über die REST-API entfernt, Pollens App neu installiert. Die Bibliothek war
  danach wieder passend. Gelesen: Der Daemon gleicht sie beim Start an seine eigene Version an
  (`check_and_sync_apps_venv_sdk`); der Reachy war über Nacht aus. Gesehen haben wir diesen Schritt nicht.
- **Regel:** Auf dem Reachy sind nur die Apps installiert, die wir wirklich nutzen. Jede weitere App
  kann Pakete der gemeinsamen Umgebung tauschen.
- **Einstellungen überleben das Entfernen:** Die `.env` der App liegt im Paketordner und blieb liegen.
- **Daemon-Log:** `ws://<reachy>:8000/logs/ws/daemon` (nicht `/api/logs/...`, das gibt 403).
- **Reachy Control auf dem PC:** Das deb-Paket aktualisiert sich nicht selbst (der eingebaute Updater
  ersetzt es nicht). Neue Version von der Release-Seite von Pollen laden, Prüfsumme vergleichen, mit `apt` installieren.
- Belege liegen lokal in `~/lola-laufzeit/messung/a4/`. Issue bei Pollen: siehe `BACKLOG.md`.

## 2026-10-09 – A4: Startskript `dienste/lola_start.py`
- Python statt Shell, nur Standardbibliothek, damit es später auch unter Windows geht.
  Aufruf: `uv run python -m dienste.lola_start start` und `stop`. Der kurze Name `uv run lola-start`
  ginge nur, wenn das Projekt als Paket gebaut wird (Eintrag `[build-system]` in `pyproject.toml`); offen.
- Das Sprachmodell lauscht nur auf dem PC selbst (`127.0.0.1:8090`), die Sprachkette im Heimnetz
  (`0.0.0.0:8765`). Sie startet mit `HF_HUB_OFFLINE=1`: im Log keine Anfrage an huggingface.co (geprüft).
- Laufdaten (Prozessnummern, Logs) liegen in `~/lola-laufzeit/lauf/`, nicht im Repo.
- Der Speicher-Wächter aus A1 gehört nicht dazu; er bleibt ein Messwerkzeug.
- Gemessen am PC: Start 21 s; Grafikspeicher vorher 635 MiB, danach 9.265 MiB (llama-server 6.012 MiB,
  speech-to-speech 2.604 MiB nach dem Laden, noch ohne Gespräch).

## 2026-10-09 – Zwischenstand: Die Conversation App läuft auf dem PC (Tests mit Patrick offen)
- **Grundsatz (Patrick):** Der Reachy ist nur Körper (Mikrofon, Lautsprecher, Kamera, Motoren). Auf ihm
  läuft keine Logik von uns, später höchstens kleine Auslöser für den PC.
- **Anlass:** Auf dem Reachy schickt App 1.0.1 die Erkennungssprache „en“; speech-to-speech nimmt mit
  Parakeet nur „auto“ an und verwirft dann die ganze Sitzungs-Einstellung samt Profil und Tools. Die
  Sprache ist dort nur per Umgebungsvariable einstellbar, also nur über eine Datei auf dem Roboter.
- **Stand:** App aus GitHub, Commit `2e43e80` (Standard „auto“, Sprache einstellbar), unverändert in
  `~/lola-laufzeit/app-venv`, Reachy-Bibliothek 1.11.0 wie der Daemon. Ton und Bild kommen per WebRTC
  direkt vom Daemon. GStreamer 1.24.2 und das WebRTC-Plugin 0.14.5 waren auf dem PC schon vorhanden.
- **Geprüft ohne Patrick:** Profil und Tools kommen an, Begrüßung „Hallo! Ich bin LoLa …“, eingeschleuste
  Bitten lösen `move_head` und `dance` aus. TCP-Verbindungen der App nur zum Reachy, zur Sprachkette und
  zum Router (Port 49000, vermutlich UPnP der WebRTC-Bibliothek). CPU im Leerlauf: 55 % eines Kerns von 16.
- **Offen, mit Patrick:** Klang, sichtbare Bewegungen und Kopfwackeln, Latenz am Reachy, 21 Testsätze,
  Motortemperatur bei laufender App. `ARCHITEKTUR.md` wird erst danach geändert. Die App auf dem Reachy
  bleibt installiert, wird aber nicht mehr gestartet.
- **Beenden (Code gelesen, am Roboter gesehen):** Die App legt den Reachy beim Stoppen absichtlich nicht
  schlafen, nur über das Tool `go_to_sleep` und nach 24 Stunden Stille. Läuft sie auf dem Reachy, räumt
  danach der Daemon auf; auf dem PC tut das niemand, die Motoren blieben an. Deshalb beendet `lola_start
  stop` die App wie mit Strg+C (ihr eigener Abschluss läuft) und legt den Reachy dann über die REST-API
  schlafen und schaltet die Motoren aus.
- **Kopfwackeln:** Die App schaltet es im Daemon bei jedem Start selbst ein und beim Beenden aus (im
  Daemon-Log gesehen). Nichts zu tun. Die Warnung der Bibliothek betrifft nur ihre eigene, zweite Variante.
- **Mikrofon-Werte:** Aus der Ferne setzt die App sie nicht. Sie werden nur flüchtig geschrieben (Code
  gelesen; ob sie einen Neustart des Reachy überleben, ist nicht ausprobiert). `lola_start start` setzt
  deshalb sechs Werte über die REST-API. Den siebten (`PP_NLATTENONOFF`, Ganzzahl) lehnt der Daemon
  1.11.0 über REST ab („required argument is not an integer“); er wird nur geprüft und gemeldet.
- **Profil:** `charakter/profile/lola_deutsch/profile.md`, der Name ist LoLa. Die App liest den Ordner
  über `REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY`; das Gedächtnis der App ist aus.
- **Motortemperatur (nur Lese-Pakete, Reachy schlafend):** alle neun Motoren antworten, 25 bis 33 °C,
  der Daemon lief ohne Fehler weiter. Bei allen ist das Warn-Bit gesetzt; vermutlich die
  Spannungsmeldung, die der Daemon selbst ausblendet. Werte in `MESSUNGEN.md`.
- `dienste/lola_start.py` hat jetzt 225 Zeilen (Ziel war eher 120): dazu kamen App, Reachy-Prüfung,
  Mikrofon-Werte und Schlafenlegen.

## 2026-10-09 – A7: Ein zweites Programm kann Ton und Bild mitlesen
- **Ergebnis:** Ja. Der Daemon bedient mehrere WebRTC-Abnehmer zugleich. Ein zweites Programm auf dem PC
  (der WebRTC-Client aus der Reachy-Bibliothek, ohne Steuerverbindung) bekam Bild und Ton, während die
  Conversation App lief. Die App zeigte dabei keine zusätzlichen Fehler, ihre CPU-Last blieb gleich.
- **Kosten:** rund ein halber CPU-Kern am PC für das Mitlesen in voller Auflösung. Auf dem Reachy sinkt der
  Regeltakt des Daemons von 49 auf 46 Hz, der längste Abstand steigt von 24 auf bis zu 39 ms, ohne Fehler.
  Für die Sinne heißt das: höchstens ein Mitleser, und klären, ob eine kleinere Auflösung reicht.
- **Qualität:** Bild 1280×720 mit 29 Bildern je Sekunde, sichtbar zusammengedrückt; für „Gesicht da oder
  nicht“ in der Nähe vermutlich genug, für Einzelheiten in der Ferne nicht. Ton 16 kHz in 2 Kanälen, 3 bis
  4 % der Werte fehlten, vereinzelt Lücken bis 210 ms. Verzögerung im Bild: 0,4 bis 0,8 s bis zur
  sichtbaren Kopfbewegung, Motoranlauf eingerechnet.
- **Offen, mit Patrick:** ob LoLa hörbar weiterspricht, solange der Mitleser verbunden ist (jeder Client
  sendet einen stillen Tonstrom zum Reachy); Tonqualität bei echter Sprache; Verzögerung im Ton.
- **Nebenbefund für A6:** 2 von 14 Sätzen über `conversation.say` gingen verloren, unabhängig vom Mitleser.
  speech-to-speech meldet einen Lesefehler (`JSONDecodeError`), beendet die Sitzung, die App verbindet
  sich nach 1,4 s neu. Ursache offen.
- Messwerte in `MESSUNGEN.md`, Skripte und Protokoll auf Branch `test/a7`. Aufnahmen aus der Wohnung
  liegen nur lokal in `~/lola-laufzeit/messung/a7/`.

## Versionen (festgenagelt)
Werden in Phase 0 eingetragen (A1 und A4):

| Komponente | Version | Datum |
| --- | --- | --- |
| Reachy-Daemon / SDK | 1.11.0 (PyPI) | 2026-10-09 |
| Conversation App | 1.0.1, Hugging-Face-Stand `ddc3096` (in A3 gelesen: GitHub `2e43e80`) | 2026-10-09 |
| Reachy Control (PC) | 0.9.35 (deb) | 2026-10-08 |
| Conversation App auf dem PC (Zwischenstand) | GitHub `2e43e80`, Reachy-Bibliothek 1.11.0, GStreamer 1.24.2, gst-plugins-rs 0.14.5 | 2026-10-09 |
| speech-to-speech | Commit `8024ccf` (in A2 geprüft, in A1 installiert) | 2026-10-08 |
| llama.cpp | Commit `d81235049384534c167caea52b85a694f6103d14` (0.6.0), CUDA 12.0, gcc 12 | 2026-10-08 |
| Sprachmodell | Qwen3-8B Q4_K_M, `Qwen/Qwen3-8B-GGUF` Stand `7c41481`, SHA-256 `d98cdcbd…5745785` (nur für A1, Wahl in A5) | 2026-10-08 |
| Spracherkennung | Parakeet TDT 0.6B v3 (`nvidia/parakeet-tdt-0.6b-v3`) über nano-parakeet 0.2.1, CPU, 6 Threads | 2026-10-08 |
| Sprachausgabe | Qwen3-TTS 0.6B Base Q8_0 mit Referenzstimme „frau“ (gespeicherte Stimmdaten); faster-qwen3-tts 0.5.4, qwentts-cpp-python 0.5.0, GGUF aus `Serveurperso/Qwen3-TTS-GGUF` | 2026-10-08 |
| PyTorch | 2.14.1+cu130 | 2026-10-08 |

## 2026-10-09 – Phase 2: Werkzeuge, App-Wechsel, Uhrzeit und Wetter
Im Code der Conversation App (GitHub `2e43e80`) und des Daemons (`fbdbca3`) gelesen, am Roboter
noch ungeprüft (C0):
- **Werkzeuge:** Tool Spaces nehmen nur `*.hf.space` an und taugen damit nicht für Privates.
  Externe Werkzeuge aus `REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY` schon. Entscheidung: dünne Hüllen auf
  dem Reachy, Logik und Passwörter im Werkzeugdienst auf dem PC.
- **Hintergrund-Werkzeuge:** Jedes Werkzeug läuft im Hintergrund, Ergebnis geht ans Modell, sobald es
  fertig ist (höchstens ein Tag). Daraus wird der Timer.
- **App-Wechsel:** `POST /api/apps/start-app/{name}` verdrängt die laufende App. Rückweg einheitlich
  über eine Ausstiegsgeste (zweimal auf den Kopf tippen), die der Wächter im Zustandsstrom
  `/api/state/ws/full` erkennt. Begründung: Apps von Pollen dürfen wir nicht kopieren oder ändern,
  ein Ausstieg pro App wäre also nicht möglich. Antennen scheiden aus, die Radio-App nutzt sie.
- **Uhrzeit** im Zustandsbericht statt als Werkzeug, **Wetter** über Open-Meteo vom PC, beides ohne
  Hugging Face. **Suche:** vorerst Pollen, später SearXNG (Backlog).
- **Kalender:** Synology Calendar über CalDAV.

