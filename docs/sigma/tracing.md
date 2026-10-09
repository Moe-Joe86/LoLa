# Steckbrief aus Unit Sigma: `tracing`

Gelesen am 9. Oktober 2026 im Sigma-Code außerhalb des Repos (`soul/tracing/`, vier Dateien, rund 1.550
Zeilen, und die Stelle, die es einschaltet). **Nur gelesen, nicht am Roboter beobachtet.** Kein Sigma-Code hier.

## Was es ist
Ein Mitschreiber für Entwickler, standardmäßig aus. Er legt je Gesprächsrunde einen Datensatz an und sammelt
darin: was wahrgenommen wurde, wie der innere Zustand war, wie bewertet wurde, was entschieden wurde, jeweils
mit Begründungen in Worten. Ausgabe als eine Zeile JSON je Runde und als lesbarer Bericht. Dazu ein
Kommandozeilen-Werkzeug zum Ein- und Ausschalten.

## Welches beobachtbare Verhalten hat es erzeugt?
**Am Roboter keines, mit Absicht:** Der Mitschreiber darf nichts verändern. Für den Entwickler entstand ein
Bericht je Runde nach dem Muster „weil X gesehen, Y gefühlt, Z bewertet, deshalb Handlung A“.

## Gute Idee
- **Eine Runde, ein Datensatz:** Ursache und Handlung stehen zusammen, nicht in vier Logs verstreut.
- **Begründung in Worten** neben den Zahlen.
- **Eine Zeile JSON je Eintrag**, maschinenlesbar und mit dem Auge lesbar.
- Der Mitschreiber fließt nie in eine Entscheidung zurück.

## Ballast
- **Einhängen von außen:** Der Mitschreiber ersetzt zur Laufzeit Funktionen anderer Bausteine durch
  umhüllte Fassungen und abonniert alle Ereignisarten. Nötig war das, weil in Sigma viele Stellen Zustand
  schrieben. Ändert sich dort ein Name, schreibt er still nichts mehr.
- Einzelstück mit Sperren für mehrere Fäden, Kategorien zum Zuschalten, Zwischenspeicher, eigenes
  Kommandozeilen-Werkzeug.
- **Keine Löschfrist:** Die Datensätze enthalten Wahrgenommenes (auch Gesagtes) und bleiben liegen.

## Was fehlt LoLa ohne es?
In Phase 1 nichts. Wir haben zwei Logs als Dateien:
- **Erklär-Log** (`seele/erklaer_log.py`): jede Zustandsänderung mit Auslöser, altem und neuem Wert.
  Schutzregel 4, immer an, enthält nichts Gesagtes.
- **Anfrage-Log** (`vermittler/anfrage_log.py`): je Anfrage Bericht, entfernte Tools, Dauer; 7 Tage Frist.

**Was ab Phase 4 fehlen wird:** die Klammer um eine Runde. Welche Wahrnehmung führte zu welcher Bewertung,
welcher Tendenz, welchem Bericht in welcher Anfrage? Heute gibt es weder Bewertung noch Auswahl, also auch
nichts zu verklammern.

## Wie passt es in unseren Kreislauf?
Wir brauchen kein Einhängen von außen: Zustand schreibt nur `seele/zustand.py` (Kreislauf-Regel 2), und
diese eine Stelle schreibt selbst ins Erklär-Log (Regel 6). Das Log ist bei uns kein Entwicklerwerkzeug zum
Zuschalten, sondern eine Schutzregel.

## Vorschlag: streichen, eine Idee vormerken
- **Streichen:** das Modul, das Einhängen, das Kommandozeilen-Werkzeug, die Kategorien.
- **Vormerken für Phase 4** (nicht jetzt bauen): eine gemeinsame Runden-Kennung in Erklär-Log und Anfrage-Log,
  und die Auswahl schreibt ihre Begründung in einem Satz dazu. Erst wenn bei einer echten Fehlersuche
  die Zuordnung über die Uhrzeit nicht reicht.

## Entscheidung
**Entscheidung Patrick, 9. Oktober 2026: streichen.** Die Runden-Kennung für beide Logs steht im BACKLOG
für Phase 4.
