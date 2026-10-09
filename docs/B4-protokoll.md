# B4 – Vermittler in der echten Kette, ohne Roboter (9. Oktober 2026)

Nur Branch `test/b4`, wird nie gemergt. Rohdaten lokal in `~/lola-laufzeit/messung/b4/`.
Vorab-Ja von Patrick: keine neue Abhängigkeit, Budgets, Tests grün. Probe am Roboter später mit A4 Teil 2.

## Plan in drei Sätzen (vor Beginn geschrieben)
1. **Was ich tue:** `lola_start` startet den Vermittler als viertes Programm zwischen Sprachmodell und
   Sprachkette (speech-to-speech → Vermittler :8091 → llama.cpp :8090) und bekommt eine Aktion, die nur
   die Kette ohne App startet; dann spielt ein Messprogramm die Rolle der App an der echten
   Realtime-Schnittstelle von speech-to-speech, mit dem Profil, den Tools und den Aufnahmen aus A1.
2. **Welche Dateien:** auf `entwicklung` `dienste/lola_start.py` mit Tests, `.env.example`, README,
   MESSUNGEN, ENTSCHEIDUNGEN, FAHRPLAN, CHANGELOG; auf `test/b4` die Messskripte und dieses Protokoll.
3. **Wie viel:** rund 30 Zeilen in `lola_start`, rund 250 Zeilen Messskripte; kein Roboter, der Reachy
   bleibt im Schlaf, weil die App nicht gestartet wird.

Gemessen wird:
- **Zwischenspeicher:** ein Gespräch über mehrere Runden; je Anfrage, wie viele Eingabe-Token llama.cpp neu
  rechnet (aus seinem Log), mit und ohne Vermittler.
- **Zusatzzeit:** dieselbe Anfrage abwechselnd direkt an llama.cpp und über den Vermittler, Zeit bis zum
  ersten Stück der Antwort. Ziel unter 20 ms.
- **Tool-Aufrufe:** die 9 Bitten aus A3, je 3 Läufe, neues Gespräch und mit Verlauf, als Text über die
  Realtime-Schnittstelle (so sendet auch `conversation.say`).
- **Abbruch:** lange Antwort anfordern, Verbindung schließen, messen, wann llama.cpp aufhört.
- **`wiederholt`:** die 20 Aufnahmen als Ton einspielen; Anfrage-Log mit dem Log von speech-to-speech
  vergleichen (dessen Meldungen zu verworfenen vorgreifenden Anfragen).

## Ablauf und Ergebnis (10:34 bis 10:53 Uhr)
- `lola_start kette` startet Sprachmodell, Vermittler und Sprachkette; der Reachy blieb im Schlaf (Motoren aus).
- Messprogramm `tests/b4/rolle_app.py` spielt die App an `ws://127.0.0.1:8765/v1/realtime`: Sitzung mit dem
  Profil und den neun Tools (aus dem Quelltext der App gelesen), Sätze als Text oder als Ton im Echtzeit-Takt.
- **Tools** (`tools_messen.py`): neues Gespräch 27/27, mit Verlauf 24/27 (dreimal „Was siehst du gerade?“ ohne Kamera).
- **Zwischenspeicher** (`zwischenspeicher.py`): mit Vermittler 71 bis 152 neu gerechnete Token je Anfrage,
  ohne 27 bis 81, bei rund 1.900 bis 2.200 Token Kontext.
- **Zusatzzeit** (`zusatzzeit.py`, 40 Paare): Median 0,7 ms, höchstens 11,4 ms.
- **Abbruch:** llama.cpp ruht 17 bis 29 ms nach dem Schließen (direkt 11 bis 18 ms). Der erste Versuch war
  unbrauchbar, weil die Antwort mit unserem Profil nach 0,3 s fertig war; wiederholt mit einer Anweisung, die
  lange Texte verlangt (volle Antwort 12,3 s).
- **Ton** (`ton_messen.py`): 20 Anfragen für 20 Sätze, keine vorgreifende; Ende der Aufnahme bis erster Ton
  1,46 s mit und 1,41 s ohne Vermittler. „Ja.“ ohne Antwort.
- **Sprechpause** (`pause_messen.py`): bei 0,7 s Pause eine verworfene und eine neue Anfrage, 2,7 s auseinander,
  Text neu erkannt („Hi, sir, Patrick.“ → „Ich heiße Patrick. Wie spät ist es gerade?“).

## Was die Messung am Code geändert hat (auf `entwicklung`)
1. Die Folgeanfrage nach einem Tool-Ergebnis wurde fälschlich als `wiederholt` gekennzeichnet.
2. Der Vergleich der Satzanfänge reicht nicht, weil sich der erkannte Text ändert.
3. Jetzt: gleiche Stelle im Gespräch und höchstens 5 s Abstand. Bei 10 s schlugen meine Testsitzungen im
   8-Sekunden-Takt fälschlich an.

## Nicht geprüft
Die Probe am Roboter mit echter Stimme (A4 Teil 2). Mehr als ein echter Fall einer vorgreifenden Anfrage.
