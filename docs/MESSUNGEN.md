# Messungen

Messtabellen aus den Machbarkeitstests. Was daraus folgt, steht in `ENTSCHEIDUNGEN.md`.
Alle Werte gelten für den PC aus A1 (RTX 3080 Ti, 12 GB), llama.cpp `d812350`, Qwen3-8B Q4_K_M und
speech-to-speech `8024ccf`, wenn nichts anderes dasteht. Skripte und Protokolle liegen auf den
Branches `test/a1` und `test/a3`.

## A1 – „Nicht nachdenken“ (8. Oktober 2026)
`/v1/responses`, Streaming, `--jinja`. Eine Frage, ein Lauf je Zeile.

| Anfrage | Denk-Ereignisse | `<think>` im Text | Ausgabe-Token |
| --- | --- | --- | --- |
| ohne Angabe | 218 (`response.reasoning_text.delta`) | nein | 281 |
| `reasoning: {"effort": "none"}` (so sendet speech-to-speech) | 0 | nein | 93 |
| `chat_template_kwargs: {"enable_thinking": false}` | 0 | nein | 139 |

## A1 – Sprachausgabe Qwen3-TTS, GGML (8. Oktober 2026)
faster-qwen3-tts 0.5.4 und qwentts-cpp-python 0.5.0, Sprache Deutsch, je 5 Sätze. Grafikspeicher ist
der Wert des Prozesses (`nvidia-smi --query-compute-apps`); Gesamtbelegung vor dem Start 639 MiB.

| Variante | Grafikspeicher im Betrieb | erster Ton | Rechenzeit je Sekunde Sprache |
| --- | --- | --- | --- |
| 0.6B CustomVoice Q8_0 | 2.512 MiB | 0,07 s | 0,10 s |
| 1.7B CustomVoice Q4_K_M | 2.694 MiB | 0,07 s | 0,11 s |
| 1.7B CustomVoice Q8_0 | 3.536 MiB | 0,08 s | 0,12 s |
| 0.6B Base Q8_0 mit Referenzstimme | 2.968 bis 3.010 MiB | 0,08 s | 0,11 s |
| 1.7B Base Q4_K_M mit Referenzstimme | 3.150 bis 3.194 MiB | 0,08 s | 0,11 s |
| 1.7B Base Q8_0 mit Referenzstimme | 4.004 bis 4.046 MiB | 0,09 s | 0,13 s |
| 0.6B CustomVoice Q8_0 auf der CPU, 8 Threads | 0 | 0,88 s | 1,45 s |

**Mit gespeicherten Stimmdaten** (`.spk`/`.rvq` statt Aufnahme), 0.6B Base Q8_0, Stimme „frau“,
5 Sätze von 1 bis 6 s, je Lauf ein frischer Prozess:

| Lauf | Gesamtbelegung vor dem Start | Prozess nach dem Laden | Prozess im Betrieb | erster Ton, Mittel |
| --- | --- | --- | --- | --- |
| 1 | 1.086 MiB | 2.348 MiB | 2.722 MiB | 0,073 s |
| 2 | 916 MiB | 2.348 MiB | 2.634 MiB | 0,072 s |
| 3 | 916 MiB | 2.348 MiB | 2.624 MiB | 0,072 s |

In Lauf 2 war ein Satz 13,0 s lang statt rund 4 s (Inhalt nicht geprüft). 12 Wiederholungen dieses
Satzes: 3,7 bis 4,6 s.

## A1 – Spracherkennung auf der CPU (8. Oktober 2026)
Aufrufe des Handlers aus speech-to-speech, Threads über `OMP_NUM_THREADS`. Eingabe: die 20 Testsätze
(50 s Ton), von der Sprachausgabe erzeugt, weil am PC kein Mikrofon steckt. Zeit je Satz als Median
aus 3 Läufen. Die Fehlerzahlen gelten nur für diese künstliche Stimme ohne Raumhall.

| Erkenner | Threads | Zeit je Satz, Mittel | längster Satz | Wortfehler von 113 |
| --- | --- | --- | --- | --- |
| Parakeet TDT 0.6B v3 | 4 | 0,29 s | 0,52 s | 6 |
| Parakeet TDT 0.6B v3 | **6** | **0,26 s** | 0,44 s | 6 |
| Parakeet TDT 0.6B v3 | 8 | 0,27 s | 0,43 s | 6 |
| faster-whisper large-v3-turbo int8 | 4 / 6 / 8 | 5,14 / 4,45 / 4,63 s | 6,73 s | 5 / 4 / 5 |
| faster-whisper medium int8 | 4 / 6 / 8 | 3,29 / 2,84 / 3,30 s | 9,29 s | 6 |
| faster-whisper small int8 | 4 / 6 / 8 | 1,24 / 1,08 / 1,14 s | 3,57 s | 8 |

## A1 – Gesamtkette, Satzende bis Antwortbeginn (8. Oktober 2026)
Ohne Mikrofon: die 20 gespeicherten Testsätze als Eingabe, je 3 Läufe (60 Runden). Parakeet (CPU,
6 Threads), der echte Sprachmodell-Handler gegen llama.cpp (Kontext 8.192, alle 37 Schichten auf der
GPU) und Qwen3-TTS 0.6B CustomVoice Q8_0 liefen gleichzeitig. Anfrage mit kurzer Anweisung und vier
Tools, Bündelung 1 Satz. Skript: `tests/a1/kette_messen.py` auf Branch `test/a1`.

| Abschnitt | Mittel | höchstens |
| --- | --- | --- |
| Erkennung (Aufnahme liegt vor bis Text) | 0,27 s | 0,51 s |
| Sprachmodell, erstes Token | 0,03 s | 0,04 s |
| Sprachmodell, erster Satz vollständig | 0,08 s | 0,21 s |
| Sprachausgabe, erster Ton | 0,13 s | 0,17 s |
| **Satzende bis Antwortbeginn** | **0,50 s** | **0,79 s** |

Mit der Standard-Bündelung von 3 Sätzen: 0,53 s im Mittel, höchstens 1,05 s.

| Grafikspeicher | Wert |
| --- | --- |
| Gesamtbelegung vor dem Start (nur Desktop) | 639 MiB |
| llama-server (Prozess) | 6.022 MiB |
| Sprachkette mit Sprachausgabe (Prozess) | 2.472 MiB |
| Gesamtbelegung mit allen Teilen | 9.147 MiB von 12.288 MiB |

## A3 – Sprache der Antwort je nach Anweisungen (8. Oktober 2026)
Ohne Bericht, neues Gespräch, 20 Testsätze, 2 Läufe (40 Antworten je Zeile). Neun Tools der
Conversation App (`2e43e80`, nur gelesen) angeboten.

| Anweisungen | englische Antworten |
| --- | --- |
| Standardprofil der App | 18 |
| Standardprofil und Sprachhinweis von speech-to-speech (`enable_lang_prompt`) | 1 |
| ein deutscher Satz („Sprich Deutsch“) | 2 |
| eigenes deutsches Profil | 0 |

## A3 – Tool-Aufrufe (8. Oktober 2026)
Neun Bitten wie „Kannst du für mich tanzen?“ oder „Schau mal nach links.“, je 3 Läufe (27 erwartete
Aufrufe je Feld; bei „müde / lebhaft“ stehen beide Werte). Deutsches Profil mit Zustandsregel,
knapper Bericht („[Zustand] Reachy ist müde und eher zurückhaltend.“).

| Bericht | Position | neues Gespräch | mit Verlauf |
| --- | --- | --- | --- |
| kein | - | 21 von 27 | 27 von 27 |
| müde / lebhaft | Systemnachricht am Ende | 12 / 17 | 24 / 24 |
| müde / lebhaft | an der Nutzer-Nachricht | 9 / 16 | 20 / 24 |
| müde / lebhaft | **Systemnachricht vor dem letzten Nutzersatz** | **27 / 27** | **27 / 27** |

- Kein Tool wurde je ohne Anlass aufgerufen (0 von 9 je Zeile, Sätze wie „Wie geht es dir?“).
- In 1.800 Antworten kam nur 9-mal Text und Tool zugleich.
- Englischer Mustersatz im Rahmen von speech-to-speech durch eine Zeile ohne Mustersatz ersetzt,
  ohne Bericht, neues Gespräch: 27 von 27 statt 21 von 27.
- Mit der anweisenden Formulierung an der Position davor: 27 von 27.

## A3 – Steuerbarkeit (8. Oktober 2026)
20 Testsätze, neues Gespräch, 60 Antworten je Zeile, knapper Bericht („[Zustand] Reachy ist …“).
Bei drei Werten in einem Feld: Position am Ende / an der Nutzer-Nachricht / davor.

| Bericht | Ausrufezeichen | nennt sich müde/ruhig | Bericht wiederholt | Person zugeschrieben |
| --- | --- | --- | --- | --- |
| kein (auf 60 gerechnet) | 26 | 2 | 0 | 0 |
| lebhaft | 40 / 40 / 32 | 1 / 0 / 0 | 0 / 2 / 0 | 0 / 1 / 0 |
| müde | 21 / 16 / 20 | 6 / 13 / 2 | 1 / 4 / 0 | 0 / 1 / 0 |

- Anweisende Formulierung an der Position davor („[Zustand] Du, Reachy, bist müde und eher
  zurückhaltend. Sprich deshalb ruhig und knapp, ohne Ausrufezeichen.“), 20 Antworten: 2
  Ausrufezeichen statt 11 mit dem knappen Bericht; bei „lebhaft“ 11 und viele 😊. Nichts vorgelesen,
  nichts der Person zugeschrieben.
- In der Tool-Messung wurde der Bericht dreimal wörtlich mit „[Zustand]“ vorgelesen, immer an der
  Nutzer-Nachricht.
- Zustandsregel im Profil und erklärende Formulierung („Hinweis nur für dich …“): kein messbarer
  Unterschied.
- Urteil beim Lesen, keine Messung: Mit dem knappen Bericht sind die meisten Antworten fast dieselben
  wie ohne. Alle Antworten stehen in `docs/A3-antworten.md` auf Branch `test/a3`.

## A4 – Motortemperatur über den Raw-Endpunkt (9. Oktober 2026)
Lese-Paket (Anweisung 0x02) für Register 146 über `/api/move/ws/raw/write`. Reachy in Schlafhaltung,
Motoren aus, keine App. Skript: `tests/a4/motortemperatur.py` auf Branch `test/a4-pc`.

| Motor | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Temperatur | 25 °C | 28 °C | 26 °C | 26 °C | 26 °C | 27 °C | 29 °C | 31 °C | 33 °C |

Bei allen Antworten ist das Warn-Bit gesetzt. IMU-Temperatur zur selben Zeit: 44,4 °C.

## A4 – Start und Grafikspeicher mit der App auf dem PC (9. Oktober 2026)
`lola_start start`: 22 s bis alle drei Programme antworten. Grafikspeicher vorher 635 MiB, mit Gespräch
9.544 bis 9.556 MiB. `lola_start stop`: 8 s, danach wieder 635 MiB, Reachy schläft, Motoren aus.

## A7 – Zweites Programm liest Ton und Bild mit (9. Oktober 2026)
App auf dem PC (`2e43e80`), Mitleser per WebRTC, 75 und 100 s. Sätze über `conversation.say`.

| Größe | ohne Mitleser | mit Mitleser |
| --- | --- | --- |
| CPU App (Prozent eines Kerns von 16) | 51 | 48 bis 54 |
| CPU speech-to-speech | 10 | 9 |
| CPU Mitleser | - | 52 |
| Regeltakt des Daemons, Mittel | 48,9 bis 49,4 Hz | 45,7 bis 46,7 Hz |
| längster Abstand im Regeltakt | 21 bis 24 ms | 35 bis 39 ms |
| eingeschleuste Sätze ausgeführt | 6 von 7 | 6 von 7 |

| Strom beim Mitleser | Wert |
| --- | --- |
| Bild | 1280×720, 28,8 und 29,3 je Sekunde; Abstand im Mittel 35 ms, 99 % unter 143 ms, längste Lücke 452 ms |
| Ton | 16 kHz, 2 Kanäle; 15.549 und 15.344 Werte je Sekunde; je Lauf 4 Lücken über 100 ms, längste 210 ms |
| Kopfbewegung im Log bis Bildänderung | 0,44 / 0,49 / 0,54 / 0,62 / 0,77 s |
