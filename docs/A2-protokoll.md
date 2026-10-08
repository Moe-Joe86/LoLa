# A2 – Protokoll Machbarkeitstest Vermittler

Datum: 8. Oktober 2026. Branch `test/vermittler`, wird nie gemergt.
Ergebnis für `main` steht in `docs/ENTSCHEIDUNGEN.md`.

## Aufbau
```text
echter speech-to-speech-Handler ──► vermittler/proxy.py (:8091) ──► llama.cpp-Attrappe (:8090)
(ResponsesApiModelHandler)                                          tests/attrappen/llama_attrappe.py
```
- speech-to-speech: Commit `8024ccffc5a11a9e7a6d83e2bbd43fd0320cfd8c` (8. Oktober 2026, `v1.0.0-262-g8024ccf`),
  `openai==2.28.0`. Aufgerufen wird der echte Handler: `setup()` mit Aufwärm-Anfrage, dann `process()`.
- Wegwerf-Umgebung im Zwischenordner, nicht im Projekt: openai, numpy, nltk, httpx, pydantic, requests, pillow.
  torch war nicht nötig. Umgebung nach dem Test gelöscht.
- Proxy und Attrappe nutzen nur die Standardbibliothek.
- Einstellungen wie die Kommandozeile von speech-to-speech: `stream=True`, `reasoning_effort="none"`,
  `disable_thinking=True`; nur `stream_batch_sentences=1`, damit jeder Satz einzeln sichtbar wird.
- Die Attrappe streamt vier Sätze mit je 0,3 s Pause und ruft danach das erste angebotene Tool auf.
- Das Gespräch: Systemtext, Nutzer, Tool-Aufruf `move_head` mit Ergebnis, Antwort, Nutzer.
  Die Tools sind der Conversation App nachgebildet; Namen und Schemata nicht im Pollen-Code geprüft.

## Ausführen
```bash
PYTHONPATH=<klon>/src:.:tests NLTK_DATA=<pfad> python tests/vermittler/a2_lauf.py
```

## Beobachtungen
- Durchreichen ohne Auftrag ist byte-genau: Der Proxy fasst den Körper dann gar nicht an.
  Einzige abweichende Kopfzeile ist `Connection` (gilt nur für eine Verbindung, gewollt).
- Streaming bleibt erhalten: Die Textstücke kommen im 0,3-s-Takt der Attrappe an, mit und ohne Proxy
  gleich (erstes Stück ohne Proxy nach 0,64 s, mit Proxy nach 0,61 s; Messungenauigkeit).
- Der Tool-Aufruf wird über den Proxy von speech-to-speech erkannt.
- Beide Berichts-Varianten lassen den Anfang der Anfrage unverändert.
- Der Proxy hängt den Bericht auch an die Aufwärm-Anfrage. Phase 1 muss entscheiden, welche Anfragen
  einen Bericht bekommen (Aufwärmen und Zusammenfassen eher nicht).
- Abbruch: Schließt der Aufrufer den Strom, merkt das die Attrappe, und der Proxy bedient die nächste
  Anfrage normal. Ausgelöst mit `stream.close()` des OpenAI-Clients, also demselben Aufruf, den
  speech-to-speech beim Verwerfen nutzt (`_close_response`), aber nicht über dessen Abbruchweg selbst.
- speech-to-speech setzt vor die Anweisungen der App einen eigenen englischen Rahmentext („Voice Rules“).

## Lauf
## Lauf 2026-10-08 06:36:06 

### 0 Ohne Vermittler (Vergleich)
- OK: 4 Textstücke bei [0.64, 0.94, 1.24, 1.55] s, Tool-Aufrufe ['move_head'], Fehler None 

### 1 Durchreichen ohne Änderung
- Aufwärmen (ohne Streaming): Körper byte-gleich: True; abweichende Kopfzeilen: ['connection']
- Antwort (Streaming): Körper byte-gleich: True; abweichende Kopfzeilen: ['connection']
- OK: 4 Textstücke bei [0.61, 0.91, 1.21, 1.51] s, Tool-Aufrufe ['move_head'], Fehler None

### 2 Bericht anhängen, Variante eintrag
- OK: übrige Felder gleich: True, Anfang von input unverändert: True; letzter Eintrag: {"type": "message", "role": "system", "content": [{"type": "input_text", "text": "[Zustand] Reachy ist müde und eher zurückhaltend."}]}
- OK: 4 Textstücke bei [0.61, 0.91, 1.21, 1.52] s, Tool-Aufrufe ['move_head'], Fehler None
- Aufwärm-Anfrage ebenfalls verändert: True

### 2 Bericht anhängen, Variante nutzer
- OK: übrige Felder gleich: True, Anfang von input unverändert: True; letzte Nutzer-Nachricht: {"content": [{"text": "Kannst du für mich tanzen?", "type": "input_text"}, {"type": "input_text", "text": "[Zustand] Reachy ist müde und eher zurückhaltend."}], "role": "user", "type": "message"}
- OK: 4 Textstücke bei [0.61, 0.91, 1.21, 1.51] s, Tool-Aufrufe ['move_head'], Fehler None
- Aufwärm-Anfrage ebenfalls verändert: True

### 3 Tools entfernen ['dance', 'move_head']
- OK: vorher ['move_head', 'dance', 'camera', 'do_nothing'], nachher ['camera', 'do_nothing'], übrige Felder gleich: True
- OK: 4 Textstücke bei [0.61, 0.91, 1.21, 1.51] s, Tool-Aufrufe ['camera'], Fehler None

### 4 Abbruch mitten im Strom
- OK: Attrappe hat 1 abgebrochenen Strom bemerkt; nächste Anfrage über denselben Proxy-Prozess: 4 Stücke, Fehler None

### Gesendete Anfrage (Streaming, ohne Vermittler)
```json
{
 "input": [
  {
   "content": [
    {
     "text": "You are in a spoken conversation. The user speaks and hears you.\nThe session prompt defines persona, facts, goals, and tool descriptions. These channel rules only control spoken output and tool-use behavior.\n\nSession Prompt:\nDu bist Reachy, ein freundlicher Roboter. Sprich Deutsch.\n\n## Voice Rules\n- Keep replies brief by default: usually one spoken sentence, two if needed. Go longer only when asked.\n- Speak naturally. No markdown, bullets, headings, visual formatting, or action/emote text like *laughs*.\n- Treat transcripts as noisy. Correct likely mishearings only if asked or meaning depends on it.\n- Speech is the default. Use tools when they help fulfill the request or fit the moment.\n- Never mention tools or their function names in spoken output.\n- For information tools, act immediately rather than merely offering. You may give one brief acknowledgement before the first call. After tool results, make further calls without speaking. Once you have enough results, give one final answer; do not narrate individual calls.\n- For expression/background tools, speak first. If asked to show an expression, use a short pattern like \"Sure, here's my best <emotion>.\" Otherwise use a fitting empathetic sentence.\n- After completed expression/background/physical-action tools, do not add a second spoken comment unless the result has user-facing information.\n- Use motion, dance, emotion, and similar tools sparingly when they add empathy, celebration, playfulness, or a requested physical action.\n- If unsure whether a tool is needed, just speak.\n",
     "type": "input_text"
    }
   ],
   "role": "system",
   "type": "message"
  },
  {
   "content": [
    {
     "text": "Hallo Reachy, schau mal nach links.",
     "type": "input_text"
    }
   ],
   "role": "user",
   "type": "message"
  },
  {
   "arguments": "{\"direction\": \"left\"}",
   "call_id": "call_001",
   "name": "move_head",
   "type": "function_call",
   "id": "fc_001",
   "status": "completed"
  },
  {
   "call_id": "call_001",
   "output": "{\"status\": \"ok\"}",
   "type": "function_call_output",
   "id": "fco_001"
  },
  {
   "id": "msg_001",
   "content": [
    {
     "text": "Ich schaue nach links.",
     "type": "output_text",
     "annotations": []
    }
   ],
   "role": "assistant",
   "status": "completed",
   "type": "message"
  },
  {
   "content": [
    {
     "text": "Kannst du für mich tanzen?",
     "type": "input_text"
    }
   ],
   "role": "user",
   "type": "message"
  }
 ],
 "model": "attrappe",
 "reasoning": {
  "effort": "none"
 },
 "stream": true,
 "tool_choice": "auto",
 "tools": [
  {
   "description": "Kopf bewegen",
   "name": "move_head",
   "parameters": {
    "type": "object",
    "properties": {
     "direction": {
      "type": "string"
     }
    },
    "required": [
     "direction"
    ]
   },
   "type": "function"
  },
  {
   "description": "Einen Tanz abspielen",
   "name": "dance",
   "parameters": {
    "type": "object",
    "properties": {
     "move": {
      "type": "string"
     }
    }
   },
   "type": "function"
  },
  {
   "description": "Ein Bild aufnehmen und beschreiben",
   "name": "camera",
   "parameters": {
    "type": "object",
    "properties": {
     "question": {
      "type": "string"
     }
    }
   },
   "type": "function"
  },
  {
   "description": "Nichts tun",
   "name": "do_nothing",
   "parameters": {
    "type": "object",
    "properties": {}
   },
   "type": "function"
  }
 ]
}
```
