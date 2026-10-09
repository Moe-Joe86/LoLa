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
