# Steckbrief aus Unit Sigma: `companion_dna`

Gelesen am 9. Oktober 2026 im Sigma-Code außerhalb des Repos (`soul/companion_dna.py`, 1.523 Zeilen, und
die Stellen, die es abfragen). **Nur gelesen, nicht am Roboter beobachtet:** „Verhalten“ heißt hier, was
laut Code beim Sprachmodell oder in der Bewertung ankam. Kein Sigma-Code in dieser Datei.

## Was es ist
Eine feste Datenstruktur mit rund 40 Feldern: Seriennummer und Name, vorformulierte Antworten auf Sinnfragen
(„Was bin ich?“, deutsch und englisch), neun Temperamentwerte, Werte mit Rangfolge und Konflikttabelle,
Ängste, Interessen, Meinungen, Sprechstil, Bildwelt für Vergleiche, Humor-Art und -Stärke, Entscheidungs-,
Konflikt- und Bewältigungsstil, Status- und Dominanzstreben, Abneigungen, Grenzen für den Selbstwert,
Kern-Erinnerungen. Dazu vier fertige Persönlichkeiten (beschützend, neugierig, verspielt, ruhig).

## Welches beobachtbare Verhalten hat es erzeugt?
- **Im Text ans Sprachmodell:** ein Block mit Name, Temperamentwerten, Werten, Sprechstil, Bildwelt und
  Interessen, dazu ein Satz zur Humor-Art. Daran war die Persönlichkeit erkennbar, soweit sie es war:
  worüber der Roboter gern redet und in welchem Ton.
- **In der Bewertung:** Sechs Werte (z. B. Ängstlichkeit, Belastbarkeit) verstärken oder dämpfen, wie stark
  ein Ereignis das Gefühl bewegt. Ein Wert steuert die Reaktionsstärke insgesamt.
- **Feste Antworten** auf Sinnfragen statt freier Antworten des Modells.
- **Ohne Abnehmer** (kein Aufrufer gefunden): Bewältigungsstil, Marotten, Kern-Erinnerungen. Mit genau einem
  Abnehmer, der sie nur in eine Zusammenfassung schreibt: Ängste, Meinungen. Die Humor-Stärke wird
  eingesammelt, erreicht den Text ans Modell aber nicht.

## Gute Idee
- Persönlichkeit ist **geladene, feste Daten**, die nur gelesen werden, mit zwei Abnehmern: Bewertung und Ton.
- Unbekannte Werte zählen als 0,5 und wirken dann nicht. Neue Werte lassen sich gefahrlos ausprobieren.
- **Vorlagen, die sich stark unterscheiden.** Genau das braucht B5 (zwei Charakterdateien).
- **Interessen:** zwei, drei Themen, über die der Roboter von sich aus gern spricht. Das ist Inhalt, nicht Ton.

## Ballast
Sinnfragen-Antworten, Seriennummer, Ängste, Konflikttabelle der Werte, Dominanz und Status, Selbstwert-Grenzen,
Erinnerungen in der Charakterdatei, vier Vorlagen zu je 100 Zeilen im Code statt als Datei, Umwandlungen
zwischen alten und neuen Dateiformaten. Viele Felder, die niemand liest.

## Was fehlt LoLa ohne es?
Nichts am Aufbau. Wir haben die Charakterdatei (`charakter/reachy.toml`, sieben Werte, geprüft beim Laden)
und den Bericht, der vier davon in Worte fasst. **Möglich, aber nicht gemessen:** LoLa hat nur „wie“-Werte
(gesellig, neugierig, vorsichtig, ausdauernd), keine eigenen Themen. Ob das im Gespräch fehlt, zeigt erst B5.

## Wie passt es in unseren Kreislauf?
Haben wir schon: Der Charakter ist Konfiguration, kein Modul (Kreislauf-Regel 4). Er wirkt über Bewertung
und Kosten der Auswahl, nie direkt auf den Zustand (KONZEPT). Dominanz, Selbstwert-Krisen und Bindungs-Etiketten
stehen in KONZEPT unter „bauen wir bewusst nicht“.

## Vorschlag: verkleinern (ist im Kern schon geschehen)
- **Übernehmen als Idee:** für B5 zwei Charakterdateien, die sich so deutlich unterscheiden wie Sigmas Vorlagen.
- **Kandidat, erst nach B5:** eine kurze Liste „Interessen“ in der Charakterdatei, wenn die Familie in B5
  sagt, LoLa habe nichts Eigenes zu erzählen. Vorher nicht (oberste Designregel).
- **Streichen:** alles unter „Ballast“.
