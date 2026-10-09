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
