# Protokoll B1 bis B3 (9. Oktober 2026, ohne Patrick, mit Vorab-Ja)

Die Pläne stehen hier, weil Testbranches die Protokolle halten. Gebaut wird auf `entwicklung`.

## B1 – Plan in drei Sätzen (vor Beginn geschrieben)
1. **Was ich tue:** Ich baue `seele/zustandsbericht.py` so um, dass der Bericht eine einzige Zeile mit der
   Kennung `[Zustand]` ist: „Du, LoLa, bist …“, danach die Sprechanweisung, die zu den Stufen von Laune und
   Erregung fest in derselben Tabelle steht.
2. **Welche Dateien:** `seele/zustandsbericht.py`, `tests/seele/test_zustandsbericht.py`, das Beispiel in
   `docs/KONZEPT.md`, dazu CHANGELOG, FAHRPLAN-Zeile B1 und ein kurzer Eintrag in ENTSCHEIDUNGEN.
3. **Wie viel:** rund 80 Zeilen Code und 90 Zeilen Tests, keine neue Abhängigkeit, kein Roboter.

Festlegungen, die ich dabei treffe (zum Nachlesen und Ändern):
- Kopfzeile und „Halte dich kurz“ entfallen: Die Kürze steht im Profil, die Form aus A3 hatte beides nicht.
- „Deine Art: …“ (Worte aus dem Charakter) bleibt als zweiter Satz erhalten, weil es heute schon getestet ist.
- Gemessen ist aus A3 nur „Sprich … ruhig und knapp, ohne Ausrufezeichen“. Die übrigen Bausteine der Tabelle
  sind mein Vorschlag und werden erst in B5/B6 am Modell geprüft.

**B1 erledigt** (Commit `59926c3` auf `entwicklung`). Satzform am Ende: „Sprich <Ton> und dabei <Tempo>.“

## B2 – Plan in drei Sätzen (vor Beginn geschrieben)
1. **Was ich tue:** Das Erklär-Log schreibt jeden Eintrag zusätzlich als eine Zeile JSON in eine Datei, und
   ein neues Anfrage-Log schreibt je Anfrage eine Zeile in eine Tagesdatei und löscht Tagesdateien, die
   älter als die Frist sind.
2. **Welche Dateien:** `seele/erklaer_log.py`, neu `vermittler/anfrage_log.py` (dort wird es in B3 gebraucht),
   Tests in `tests/seele/` und `tests/vermittler/`, `.env.example` (Frist), CHANGELOG, FAHRPLAN, ENTSCHEIDUNGEN.
3. **Wie viel:** rund 90 Zeilen Code und 110 Zeilen Tests, nur Standardbibliothek, kein Roboter.

Festlegungen:
- Ordner `daten/` (steht schon in `.gitignore`). Erklär-Log: `daten/erklaer-log.jsonl`, wird nicht gelöscht
  (enthält Zustandswerte und Auslöser, nichts Gesagtes). Anfrage-Log: `daten/anfragen-JJJJ-MM-TT.jsonl`.
- Löschen heißt: ganze Tagesdateien entfernen, deren Tag mehr als die Frist zurückliegt. Geprüft wird bei
  jedem Schreiben. Frist: `LOLA_ANFRAGE_LOG_TAGE`, Standard 7.
- Felder je Anfrage: Zeit, Gesagtes (letzter Nutzersatz), eingefügter Bericht, entfernte Tools, Dauer in ms.

**B2 erledigt** (Commit `4c2dca1` auf `entwicklung`): Erklär-Log als Datei, Anfrage-Log mit Tagesdateien
und Löschfrist, 13 Tests.

## B3 – Plan in drei Sätzen (NICHT gebaut, wartet auf Patricks Ja)
1. **Was ich tun würde:** Einen kleinen HTTP-Proxy `vermittler/proxy.py` bauen, der `POST /v1/responses` von
   speech-to-speech annimmt, den Zustandsbericht als eigenen Systemeintrag direkt vor den letzten Nutzersatz
   setzt, die Anfrage an llama.cpp weitergibt, die Antwort Stück für Stück zurückreicht und je Anfrage eine
   Zeile ins Anfrage-Log schreibt; alles andere geht unverändert durch.
2. **Welche Dateien:** `vermittler/proxy.py` (Server und Weitergabe), `vermittler/anfrage.py` (reine
   Funktionen: Bericht einsetzen, Tools entfernen, letzten Nutzersatz finden), eine Attrappe von llama.cpp
   in `tests/attrappen/`, Tests in `tests/vermittler/`, dazu CHANGELOG, FAHRPLAN, ENTSCHEIDUNGEN.
3. **Wie viel:** rund 220 Zeilen Code und 250 Zeilen Tests, kein Roboter; angeschlossen an die echte Kette
   wird erst in B4.

### Vorschlag zur HTTP-Bibliothek: keine. Nur die Standardbibliothek.
`http.server.ThreadingHTTPServer` für den Eingang, `http.client` für den Ausgang. So war auch der
Testproxy aus A2 gebaut (dort gegen die Attrappe und den echten Handler von speech-to-speech geprüft:
byte-genaues Durchreichen, Streaming im Takt, Abbruch mitten im Strom).

| Kriterium | Standardbibliothek (Vorschlag) | aiohttp | httpx + starlette + uvicorn |
| --- | --- | --- | --- |
| Größe | 0 neue Pakete | 1 Paket, zieht rund 7 weitere nach | 3 Pakete, ziehen rund 8 weitere nach |
| Wartung | kommt mit Python, ändert sich kaum | aktiv gepflegt, eigene Versionssprünge | drei Projekte, die zusammenpassen müssen |
| Streaming | von Hand: Zeilen lesen und sofort weiterschreiben; in A2 gezeigt | eingebaut, Server und Client aus einer Hand | eingebaut, über zwei Bibliotheken verteilt |
| Abbruch | von Hand: Schreibfehler zum Client erkennen, dann die Verbindung zu llama.cpp schließen | eingebaut (abgebrochene Anfrage beendet die Aufgabe) | eingebaut, aber je nach Server unterschiedlich zuverlässig |
| Gleichzeitigkeit | ein Faden je Anfrage; reicht, weil llama.cpp nur eine Anfrage zugleich rechnet | sehr viele gleichzeitig | sehr viele gleichzeitig |
| Risiko | Abbruch wird erst beim nächsten Schreiben bemerkt; Sonderfälle von HTTP sind Handarbeit | neue Abhängigkeit, asynchroner Stil im ganzen Vermittler | größte Abhängigkeit, am meisten bewegliche Teile |

Begründung: Der Vermittler bedient genau einen Client und einen Server im selben Rechner, mit wenigen
Anfragen zugleich. Dafür braucht es keine Bibliothek, und die Regel „keine neue Abhängigkeit“ bleibt
unberührt. Die Schwäche (Abbruch erst beim nächsten Schreiben) wird in B4 gemessen: Bricht speech-to-speech
eine vorgreifende Anfrage ab, bevor das erste Wort kommt, darf llama.cpp nicht weiterrechnen.
**Rückfallweg:** aiohttp, falls B4 zeigt, dass der Abbruch zu spät greift oder der Vermittler mehr als
20 ms kostet. Die reinen Funktionen in `vermittler/anfrage.py` blieben dabei gleich.

### Was B3 bewusst nicht enthält
- Die Deutung (zweiter Aufruf ans Sprachmodell) und das Melden von Gesagtem an die Seele: spätere Phase.
- Echte harte Grenzen: Die Funktion „Tools entfernen“ wird gebaut und getestet, aber noch von nichts ausgelöst.
- Der Zustand ändert sich in Phase 1 noch nicht; der Bericht kommt aus Charakter und Grundzustand.

### Offene Punkte, die ich vor dem Bau klären möchte
- Aufwärm- und Zusammenfassungs-Anfragen von speech-to-speech sollen keinen Bericht bekommen (Hinweis aus
  A2). Woran der Vermittler sie erkennt, muss ich am Code von speech-to-speech nachlesen.
- Vorgreifende Anfragen: Derselbe Satz kann mehrfach kommen. Für B3 heißt das nur: Jede Anfrage bekommt ihre
  Zeile im Anfrage-Log. Soll das Log solche Wiederholungen kennzeichnen?

## Verlorene `conversation.say`-Sätze – Plan in drei Sätzen (vor der Messung geschrieben)
1. **Was ich tue:** Im Code gelesen: `/rpc` läuft im Faden „ui-server“, die Verbindung zur Sprachkette im
   Hauptfaden; `conversation.say` sendet direkt aus dem fremden Faden, während dort laufend Mikrofonton
   gesendet wird. Ich messe das am Roboter mit zwei Reihen zu je 30 Sätzen: normal, und mit Mikrofon stumm
   (`conversation.mic`) für den Moment des Sendens.
2. **Welche Dateien:** `tests/a7/say_reihe.py` auf diesem Branch; Ergebnis in ENTSCHEIDUNGEN auf `entwicklung`.
3. **Am Reachy:** nur wecken und wieder schlafen legen (`lola_start`), nichts speichern; an Pollens Code und
   an speech-to-speech wird nichts geändert.

**Ergebnis say (10:05 bis 10:14 Uhr):** Abstand 4 s: 0 von 30. Abstand 20 s: 0 von 12. Abstand 0,5 s: 3 Abbrüche
in 100 (10:11:55, 10:12:05, 10:12:55). Mit stummem Mikrofon beim Senden: 0 in 100. Ursache und Vorschlag
stehen in ENTSCHEIDUNGEN auf `entwicklung`. Reachy danach schlafen gelegt.

## B3 – Ja von Patrick liegt vor (Standardbibliothek, vorgreifende Anfragen kennzeichnen, Aufräumen beim Start)
Plan wie oben. Zuerst lese ich in speech-to-speech nach, woran Aufwärm-, Zusammenfassungs- und vorgreifende
Anfragen zu erkennen sind.
