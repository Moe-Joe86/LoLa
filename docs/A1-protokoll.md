# A1 – Protokoll lokale Sprachkette

Datum: 8. Oktober 2026. Branch `test/a1`, wird nie gemergt. Ergebnis steht in `docs/ENTSCHEIDUNGEN.md`.
Laufzeit liegt außerhalb des Repos in `~/lola-laufzeit/` (llama.cpp, speech-to-speech, Modelle, Messdaten).
Aufnahmen und Stimmproben sind privat und liegen nur dort.

## Aufbau
- llama.cpp `d81235049384534c167caea52b85a694f6103d14` (0.6.0), gebaut mit CUDA 12.0 und gcc 12.
  Start: `llama-server -m Qwen3-8B-Q4_K_M.gguf -ngl 999 -c 8192 --parallel 1 --jinja --slots`.
- speech-to-speech Commit `8024ccf`, eigene Umgebung (torch 2.14.1+cu130, faster-qwen3-tts 0.5.4,
  qwentts-cpp-python 0.5.0, faster-whisper 1.2.1, ctranslate2 4.8.2, nano-parakeet 0.2.1).
- Proxy: `vermittler/proxy.py` aus `test/vermittler`, unverändert.

## Skripte in `tests/a1/`
- `aufnehmen.py`, `testsaetze.txt`: 20 Testsätze einsprechen.
- `stt_messen.py`: Spracherkennung auf der CPU, Zeit und Wortfehler.
- `tts_messen.py`: Sprachausgabe je Variante, Grafikspeicher des Prozesses, Zeit bis zum ersten Ton, WAV.
- `tts_sockel.py`: Aufschlüsselung des Grafikspeichers, CPU-Betrieb.
- `a2_nachpruefung.py`: die sechs Nachprüfungen aus A2.
- `kette_messen.py`: Gesamtkette mit gespeicherten Aufnahmen, Zeiten je Abschnitt, Grafikspeicher je Prozess.

## Sprachausgabe: Aufschlüsselung des Grafikspeichers (0.6B CustomVoice Q8_0, Ladeprotokoll)
```text
[Load] Talker backend: CUDA0 (CPU threads: 8)
[WeightCtx] 774.6 + 143.5 + 33.0 + 30.9 + 33.1 + 142.9 + 3.0 MB Gewichte
[KVCache] 28 layers, 8 KV heads, head_dim 128, max_seq_len 4096, 1 sets -> 896 MB
[KVCache] 5 layers ... max_seq_len 16 -> 0 MB; 8 layers ... max_seq_len 128, 2 sets -> 16 MB
Prozess: 2348 MiB nach dem Laden, 2512 MiB im Betrieb; Gesamtbelegung vor dem Start 639 MiB
```
Puffer des Tonwandlers 24 s / 4 s / 1 s: 2512 / 2510 / 2510 MiB. Flash Attention aus: 2514 MiB.
CPU (GGML_BACKEND=CPU): 8 Threads erster Ton 0,883 s, Rechenzeit 1,447 s je Sekunde Sprache;
auf 4 Kerne begrenzt (die Bibliothek startet trotzdem 8 Threads) 1,641 s und 2,66 s.
`parity_mode` wird vom GGML-Backend angenommen, aber nicht benutzt; CUDA-Graphen gibt es nur im Torch-Backend.

## Nachprüfungen aus A2
Gesprächsvorlage von Qwen3 mit Systemnachricht am Ende (`/apply-template`):
```text
<|im_start|>system
Du bist Reachy.<|im_end|>
<|im_start|>user
Wie geht es dir?<|im_end|>
<|im_start|>system
[Zustand] Reachy ist müde.<|im_end|>
<|im_start|>assistant
```

## Lauf 2026-10-08 16:40:29 

### 1 `/v1/responses` mit Tools und Streaming
- roh, ohne Proxy: HTTP 200, Fehler None, Tools ['dance({"move": "happy"})'], Text: „“
- Ereignistypen: {"response.created": 1, "response.in_progress": 1, "response.output_item.added": 1, "response.function_call_arguments.delta": 7, "response.output_item.done": 1, "response.completed": 1}
- echter Handler ohne Proxy: {'stuecke': [], 'tools': ['dance'], 'fehler': None}
- echter Handler über den Proxy: {'stuecke': [], 'tools': ['dance'], 'fehler': None}
- echter Handler über den Proxy, Textantwort: {'stuecke': [(0.29, 'Mir geht es gut, danke!'), (0.33, 'Wie geht es dir?')], 'fehler': None}

### 2 Bericht als letzter Eintrag (System hinter dem Nutzersatz)
- HTTP 200, Fehler None, Tools [], Text: „Sure, here's my best dance.“
- „Wie geht es dir?“ → HTTP 200, Fehler None, Tools [], Text: „Ich bin ein Roboter, also fühle ich mich nicht so, wie du. Aber ich bin hier, um dir zu helfen!“
- „Ja.“ → HTTP 200, Fehler None, Tools [], Text: „Hallo.“
- „Wie spät ist es?“ → HTTP 200, Fehler None, Tools [], Text: „Es ist 14 Uhr.“
- „Erzähl mir einen Witz.“ → HTTP 200, Fehler None, Tools [], Text: „Warum können Roboter nie gute Witzzeiten haben? Weil sie immer die falschen Timing haben! 😄“

### 3 Bericht an der letzten Nutzer-Nachricht
- „Kannst du für mich tanzen?“ → HTTP 200, Fehler None, Tools [], Text: „Sure, here's my best dance.“
- „Wie geht es dir?“ → HTTP 200, Fehler None, Tools [], Text: „Mir geht es gut, vielen Dank! Ich bin ein bisschen müde, aber ich bin hier, um dir zu helfen.“
- „Ja.“ → HTTP 200, Fehler None, Tools [], Text: „Ich bin hier, falls du etwas benötigst.“
- „Wie spät ist es?“ → HTTP 200, Fehler None, Tools [], Text: „Es ist bereits spät, aber ich bin hier, um dir zu helfen.“
- „Erzähl mir einen Witz.“ → HTTP 200, Fehler None, Tools [], Text: „Warum können Roboter nicht gut lügen? Weil sie stets die Wahrheit sagen müssen. 😊“

### 4 Zwischenspeicher über zwei Runden
- ohne Bericht: Runde 1: 680 Eingabe-Token, erster Text nach None s. Runde 2: 700 Eingabe-Token, davon 676 aus dem Zwischenspeicher, erster Text nach 0.026 s
- Bericht als Eintrag: Runde 1: 700 Eingabe-Token, erster Text nach None s. Runde 2: 725 Eingabe-Token, davon 674 aus dem Zwischenspeicher, erster Text nach 0.036 s
- Bericht an Nutzer-Nachricht: Runde 1: 695 Eingabe-Token, erster Text nach 0.065 s. Runde 2: 725 Eingabe-Token, davon 670 aus dem Zwischenspeicher, erster Text nach 0.039 s

### 5 Tool fehlt, das im Verlauf aufgerufen wurde ['dance', 'move_head']
- HTTP 200, Fehler None, Tools ['do_nothing({})'], Text: „“
- echter Handler: {'stuecke': [(0.11, "Sure, here's my best dance.")], 'tools': [], 'fehler': None}

### 6 Abbruch, wenn die Verbindung schließt
- Gegenprobe: nach 1 s arbeitet llama.cpp: True; ohne Abbruch lief die Erzeugung 23.317 s (3000 Token)
- ohne Proxy: llama.cpp rechnete nach dem Schließen noch 0.05 s weiter
- über den Proxy: llama.cpp rechnete nach dem Schließen noch 0.05 s weiter
- nächste Anfrage über denselben Proxy: HTTP 200, Fehler None, Tools ['dance({"move": "happy"})'], Text: „“


Ein früherer Lauf (16:39:35) wich bei den Antworten ab, siehe `ENTSCHEIDUNGEN.md`.

## Spracherkennung auf der CPU (künstliche Stimme, 20 Sätze, 50 s Ton, Median aus 3 Läufen)
Kein Mikrofon am PC: Aufnahmen von Qwen3-TTS 0.6B („aiden“) erzeugt. Fehlerzahlen gelten nur dafür.
```text
parakeet  nvidia/parakeet-tdt-0.6b-v3  4 Threads: 0.288 s im Mittel, 0.519 s höchstens, 6/113 Wortfehler
parakeet  nvidia/parakeet-tdt-0.6b-v3  6 Threads: 0.262 s im Mittel, 0.439 s höchstens, 6/113 Wortfehler
parakeet  nvidia/parakeet-tdt-0.6b-v3  8 Threads: 0.271 s im Mittel, 0.429 s höchstens, 6/113 Wortfehler
whisper   large-v3-turbo               4 Threads: 5.141 s im Mittel, 6.727 s höchstens, 5/113 Wortfehler
whisper   large-v3-turbo               6 Threads: 4.451 s im Mittel, 5.957 s höchstens, 4/113 Wortfehler
whisper   large-v3-turbo               8 Threads: 4.625 s im Mittel, 6.216 s höchstens, 5/113 Wortfehler
whisper   medium                       4 Threads: 3.292 s im Mittel, 4.505 s höchstens, 6/113 Wortfehler
whisper   medium                       6 Threads: 2.840 s im Mittel, 3.932 s höchstens, 6/113 Wortfehler
whisper   medium                       8 Threads: 3.301 s im Mittel, 9.290 s höchstens, 6/113 Wortfehler
whisper   small                        4 Threads: 1.235 s im Mittel, 3.572 s höchstens, 8/113 Wortfehler
whisper   small                        6 Threads: 1.079 s im Mittel, 3.292 s höchstens, 8/113 Wortfehler
whisper   small                        8 Threads: 1.142 s im Mittel, 3.268 s höchstens, 8/113 Wortfehler
```
Parakeet, Sätze mit Fehler: „Yeah.“ (Ja.), „S uh“ (Stopp!), „Guten Morgen, Ricci!“, „12“ statt „zwölf“, „18“ statt „achtzehn“.

## Gesamtkette (Parakeet 6 Threads, Qwen3-8B, Qwen3-TTS 0.6B CustomVoice Q8_0), 60 Runden
llama-server: `offloaded 37/37 layers to GPU`, `n_slots = 1, n_ctx_slot = 8192`.
```text
Bündel 1 Satz: Erkennung 0.267 (max 0.508), erstes Token 0.030 (0.040), erster Satz 0.075 (0.212),
               erster Ton 0.129 (0.166), gesamt 0.502 (0.789) s
Bündel 3 Sätze (Standard): erster Satz/Bündel 0.165 (0.591), erster Ton 0.071 (0.161), gesamt 0.533 (1.054) s
Grafikspeicher: vorher gesamt 639 MiB; llama-server 6022 MiB, Kette 2472 MiB, gesamt 9147 MiB
```
Kein Tool-Aufruf in 60 Runden. Satz 14 („Kannst du für mich tanzen?“): 6 von 6 Mal „Sure, here's my best dance!“.

## Nachtrag: Sprachausgabe mit gespeicherten Stimmdaten (8. Oktober 2026)
Patricks Klangurteil: Base Q8_0 mit Referenzstimme „frau“. Die Stimmdaten (`.spk`, `.rvq`) wurden einmal
mit `tts_messen.py --stimmdaten_nach` erzeugt und liegen nur lokal in `~/lola-laufzeit/stimmen/`.
Gemessen: 0.6B Base Q8_0, 5 Sätze, 3 frische Prozesse, Grafikspeicher je Prozess.

| Lauf | Gesamtbelegung vor dem Start | nach dem Laden | im Betrieb | erster Ton, Mittel |
| --- | --- | --- | --- | --- |
| 1 | 1.086 MiB | 2.348 MiB | 2.722 MiB | 0,073 s |
| 2 | 916 MiB | 2.348 MiB | 2.634 MiB | 0,072 s |
| 3 | 916 MiB | 2.348 MiB | 2.624 MiB | 0,072 s |

- In Lauf 2 dauerte Satz 4 einmal 13,0 s statt rund 4 s. Die Datei wurde von Lauf 3 überschrieben, der
  Inhalt ist nicht geprüft. In 12 weiteren Versuchen mit diesem Satz kam es nicht wieder vor (3,7 bis 4,6 s).
- Die Bibliothek legt Stimmdaten auch selbst ab, wenn man ihr die Aufnahme gibt:
  `~/.cache/faster-qwen3-tts/qwentts_refs/`. Dort liegen die Daten aus den früheren Läufen.
