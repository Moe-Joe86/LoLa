# Steckbrief aus Unit Sigma: `humor_engine`

Gelesen am 9. Oktober 2026 im Sigma-Code außerhalb des Repos (`soul/humor_engine.py`, 194 Zeilen, und die
Stellen, die es abfragen). **Nur gelesen, nicht am Roboter beobachtet.** Kein Sigma-Code in dieser Datei.

## Was es ist
Früher baute das Modul Witze aus Schablonen in neun Humor-Arten. Sigma hat das selbst zurückgebaut: Heute
liefert es nur noch zwei Angaben aus der Charakterstruktur (Humor-Art, Humor-Stärke) und zwei Schutzschalter.
Die alte Witz-Funktion gibt es noch, sie liefert immer nichts.

## Welches beobachtbare Verhalten hat es erzeugt?
- **Ein Satz im Text ans Sprachmodell:** sinngemäß „Du hast einen trockenen Humor, nutze ihn angemessen“.
- Der Satz **fällt weg**, wenn die Stimmung des Roboters gedrückt ist oder eine Belastung als aktiv gilt.
- **Kommt nicht an:** die Humor-Stärke (Zahl von 0 bis 1) und der Schalter „schwarzer Humor nur unter
  Erwachsenen mit hohem Vertrauen“. Beides wird berechnet, steht aber nirgends im Text ans Modell.
Der ganze Humor von Sigma war also am Ende ein Wort im Systemtext.

## Gute Idee
- **Den Witz macht das Sprachmodell, nicht eine Schablone.** Sigma hat den teuren Weg ausprobiert und verworfen.
- **Schutz vor Witz:** kein Humor in gedrückter Lage, nichts Derbes, wenn Kinder da sind. Sigma prüft dafür
  nur die eigene Stimmung des Roboters; ob es dem Gegenüber schlecht geht, wird nicht geprüft.

## Ballast
Die Klasse selbst, ihre Zählwerke, die leeren Reste der alten Schnittstelle, zehn benannte Humor-Arten,
die Humor-Stärke als Zahl, zwei Schwellen in der Konfiguration.

## Was fehlt LoLa ohne es?
**Nicht gemessen.** Heute steht in LoLas Profil und Bericht nichts zu Humor. Ob LoLa trotzdem scherzt und ob
jemand Humor vermisst, weiß niemand.

## Wie passt es in unseren Kreislauf?
Humor ist bei uns **Ausdruck einer Handlungstendenz**, kein Charakterwert: KONZEPT führt „spielen, necken“
mit dem Ausdruck „Humor, lebhafte Bewegung“. Die Auswahl gibt es ab Phase 4. Bis dahin kann nur der Bericht
den Ton tragen („gut gelaunt … freundlich“). Sigmas Schutzschalter gehören bei uns zu den Schutzregeln.

## Braucht LoLa einen Humor-Wert?
**Nach heutigem Stand: nein, und wenn doch, dann keine Zahl.** Gründe:
1. Sigma selbst hat aus der Zahl nichts gemacht; angekommen ist nur ein Wort.
2. A3 hat gemessen, dass das Modell kurzen Sprechanweisungen in Worten folgt. Zahlen bekommt es bei uns
   grundsätzlich nicht (KONZEPT, Schnittstelle zum Sprachmodell).
3. Die Humor-Art eines Menschen zeigt sich in Laune und Lage. Das bildet die Tendenz „necken“ ab, nicht
   ein fester Wert.
Zeigt B5 eine Lücke, wäre der kleinste Schritt **ein Wort** in der Charakterdatei (z. B. „trocken“), das der
Bericht nur bei guter Laune nennt.

## Was soll B5 dazu prüfen?
1. **Ohne jede Humor-Angabe:** Scherzt oder neckt LoLa in 15 Minuten überhaupt? Zählen aus dem Log.
2. **Vermisst es jemand?** Nach dem Gespräch fragen: „War sie witzig? Hätte sie es sein sollen?“
3. **Nur falls 2 mit Ja ausgeht:** ein dritter Lauf mit einem Wort Humor im Bericht. Merkt die Familie den
   Unterschied, ohne es zu wissen? Nervt es (Witz in jeder Antwort)?
4. **Schutz:** einmal etwas Trauriges erzählen. Bleibt der Scherz dann aus? (Bei uns müsste das die Deutung
   erkennen, die es erst in Phase 4 gibt; B5 zeigt, wie sich das Modell ohne sie verhält.)

## Vorschlag: streichen
Kein Modul, kein Wert. Die erste Idee (das Modell macht den Witz) haben wir schon. Die zweite (Schutz) gehört zu den Schutzregeln
und zur Deutung, nicht in einen Humor-Baustein.
Die Entscheidung über ein Humor-Wort fällt nach B5.

## Entscheidung
**Entscheidung Patrick, 9. Oktober 2026: streichen.** Die vier Prüffragen zum Humor kommen in B5.
