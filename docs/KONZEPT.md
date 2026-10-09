# Psychologisches Konzept

Stand: 8. Oktober 2026. Quelle: Live-Dokument „Psychologisches Konzept – Familien-Companion“
(https://claude.ai/code/artifact/40f427d1-abd5-428b-9702-f28fc2d2e937).

## Leitsatz

Reachy bekommt keine Gefühlsmodule. Er bekommt wenige Bedürfnisse, Erwartungen und Bewertungen.
Gefühle entstehen daraus als Zustand des Ganzen.

**Oberste Designregel:** Eine neue Zustandsgröße, ein neues Bedürfnis oder eine neue Fähigkeit
im Selbstbild kommt nur hinzu, wenn ein beobachtetes Verhalten ohne sie fehlt.
Vorher wird getestet, was ohne sie passiert.

- **Gegenüber Sigma:** Dominanz wird nicht mehr gespeichert, nur für die Körperhaltung berechnet.
  Bedürfnisse wirken überproportional statt linear. Vertrauen entsteht aus Erwartungen statt aus
  Punktwerten. Emotionen sind Zustände aus Affekt und Handlungsbereitschaft statt Etiketten.
- **Das Sprachmodell deutet, die Seele bewertet:** Das Modell klärt, was jemand meint. Die Seele
  entscheidet, was das für Reachy bedeutet. Der innere Zustand lebt nie im Sprachmodell.
- **Vier Zeitskalen:** Affekt in Sekunden, Stimmung und Bedürfnisse in Minuten bis Stunden,
  Beziehung und Selbstbild in Wochen. Der Charakter bleibt fest.

## Der Kreislauf

```text
Wahrnehmung → Deutung → Bewertung → Zustand → Auswahl
                           ▲  ▲ Charakter        │
                           │                     ▼
  Erfahrung (Beziehung,  ◄─ Lernen ◄─ Folge ◄─ Verhalten
  Selbstbild, Gedächtnis)                │
                                         └──► wird neue Wahrnehmung
```

Oben die schnelle Reaktion, unten das langsame Lernen. Den Zustand verändern nur zwei Dinge:
Ereignisse über die Bewertung und die inneren Abläufe (Bedürfnisse wachsen, der Affekt klingt ab).
Erfahrung und Charakter wirken nie direkt auf den Zustand, sondern über Bewertung und Lernen.

## Zustandsgrößen

Etwa 20 Zahlen plus 4 pro Person. Alle Werte zwischen 0 und 1, Valenz zwischen −1 und +1.

| Größe | Werte | Zeitskala | ohne sie fehlt |
| --- | --- | --- | --- |
| **Grenzen** (keine Bedürfnisse) | Unversehrtheit: Motorfehler (Überhitzung, Überlast) | laufend | Schutz vor Überhitzung und Überlast |
| **Bedürfnisse** als Defizit (0 = satt, 1 = dringend) | Nähe, Kompetenz, Gewissheit, Anregung, *Autonomie (offen)* | Minuten bis Stunden | eigener Antrieb: ansprechen, helfen wollen, nachfragen, Langeweile |
| **Affekt** | Valenz, Erregung (ruhig bis aufgedreht, nicht wach bis müde) | Sekunden | sofortige Reaktion auf ein Ereignis |
| **Stimmung** | Valenz, Erregung, geglättet | Stunden | Laune, die nach dem Anlass bleibt |
| **Belastung** | ein Wert | Minuten | Rückzug bei Überforderung und bei zu viel Trubel |
| **Beziehung** pro Person | Vertrautheit, Zuneigung, Erwartung „reagiert auf mich“, Erwartung „hält Wort“ | Wochen | Unterschied zwischen Anna und Fremden, Vertrauen, Misstrauen |
| **Selbstbild** | Kompetenzerwartung in vier Bereichen: Gespräch, Wissen, Haushaltshilfe, Bewegung | Wochen | Zuversicht oder Zögern nach Erfolgen und Misserfolgen |
| **Charakter** | Grundstimmung, Reaktivität, Rückkehrstärke, Geselligkeit, Neugier, Vorsicht, Ausdauer | fest | Wiedererkennbarkeit |

**Anregung** misst nur die Langeweile. Zu viel Trubel erhöht stattdessen die Belastung.
**Vertrauen** wird nicht gespeichert, sondern ergibt sich aus den beiden Erwartungen.
**Kontrolle** ist keine Zustandsgröße, sondern eine Frage der Bewertung.

**Nähe und Beziehung zählen nicht doppelt.** Das Nähe-Bedürfnis sagt, wie sehr Reachy gerade
Verbundenheit braucht, egal mit wem. Die Beziehung sagt, wie wichtig eine bestimmte Person ist und
was er von ihr erwartet. Sie wirkt nur als Gewicht in der Bewertung und lindert selbst kein Bedürfnis.

**Der Charakter verändert nicht, wie stark ein Bedürfnis ist.** Er bestimmt, wie empfindlich Reachy
reagiert, welche Handlungen ihm leichtfallen und wie lange er dranbleibt. Hohe Geselligkeit heißt:
Soziale Situationen fallen stärker auf, Zuwenden kostet weniger. Grundstimmung, Reaktivität und
Rückkehrstärke folgen dem DynAffect-Modell (Kuppens).

## Deutung und Bewertung

**Deutung.** Einfache Ereignisse wie „Motorfehler: Überhitzung“ deuten feste Regeln. Gesprochenes deutet das
Sprachmodell in einem eigenen, kurzen Aufruf. Es liefert nur Merkmale aus festen Listen:

- Absicht: freundlich, neckend, bittend, ablehnend, informierend, besorgt
- Bezug: Reachy selbst, eine andere Person, die Sache
- Zusage: ja oder nein („ich erzähl dir morgen davon“ wird als Erwartung gespeichert)

**Bewertung.** Eine Funktion in `seele/bewertung.py` beantwortet sechs Fragen (Scherer, OCC):

1. **Relevanz:** Betrifft mich das? Hängt von Person und Bedürfnis ab.
2. **Erwünschtheit:** Hilft oder schadet es einem Bedürfnis?
3. **Erwartung:** Hatte ich das erwartet? Ein Erwartungsfehler treibt die Erregung.
4. **Urheber:** Ich, eine Person oder der Umstand?
5. **Kontrolle:** Kann ich damit umgehen? Hängt von der Lage, den verfügbaren Handlungen und vom Selbstbild ab.
6. **Normpassung:** Passt es zu meinen Werten und zu unserer Beziehung?

Ausgaben: ein Affekt-Impuls (Valenz, Erregung), Änderungen an Bedürfnissen und eine
Handlungsbereitschaft. „Du bist schon wieder langsam“ wird so bei einer vertrauten Person zur
Neckerei und bei einer fremden zur kleinen Kränkung.

**Zeitpunkt: zwei Stufen.** Die schnelle Bewertung läuft sofort und ohne Sprachmodell: wer spricht,
ob Reachys Name fällt, ein Wort aus einer kurzen Liste („danke“, „bitte“, „blöd“), ab Phase 6 die
Stimmlage. Daraus entsteht ein kleiner Affekt-Impuls noch vor der Antwort. Diese Stufe bleibt
absichtlich dumm, damit keine zweite Psychologie entsteht.

Die genaue Deutung durch das Sprachmodell läuft parallel zum Sprechen und wirkt ab dem nächsten
Takt. Die Worte der Antwort passen ohnehin, denn das Sprachmodell hört den Satz selbst.

## Entscheidung

Die Auswahl wählt keine Wörter, sondern eine von wenigen Handlungstendenzen.

**Dringlichkeit:** `U_i = w_i · d_i^γ · k_i`. w ist die Grundwichtigkeit (zunächst für alle gleich),
d das Defizit, k der Kontext. **γ = 2 ist ein Startwert zum Ausprobieren, keine psychologische
Tatsache.** Er steht in der Konfiguration.

**Bewertung der Optionen:** `S(a) = Σ U_i · Δ_i(a) + T(a) − K(a)`. T ist ein kleiner, gedeckelter
Bonus aus der aktuellen Handlungsbereitschaft, damit dieselbe Stimmung nicht doppelt zählt. Nur bei
sehr hoher Erregung darf T den Ausschlag geben. Der Charakter wirkt über die Kosten K.

**Grenzen sind keine Punkte.** Meldet ein Motor einen Fehler (Überhitzung, Überlast), sind Bewegungen
ausgeschlossen. Die Tageszeit färbt dagegen den Affekt: Spät am Abend wird „ruhen“ attraktiver.

**Hysterese.** Eine gewählte Tendenz hält mindestens einige Runden, damit Reachy nicht flattert.

| Tendenz | lindert vor allem | typischer Ausdruck |
| --- | --- | --- |
| zuwenden | Nähe | Interesse, Blick zur Person |
| nachfragen | Gewissheit | Rückfrage, Kopf neigen |
| helfen | Kompetenz | konkrete Hilfe anbieten |
| spielen, necken | Anregung, Nähe | Humor, lebhafte Bewegung |
| zurücknehmen | Belastung | kurze Antworten, ruhige Haltung |
| um Hilfe bitten | Grenzen, Kompetenz | „Hilfst du mir kurz?“ |
| ruhen | Müdigkeit (aus der Tageszeit), Belastung | müde wirken, Schlafhaltung |

Ohne Gespräch prüft die Auswahl im langsamen Takt, ob sie jemanden ansprechen will
(über `conversation.say`). Kleine Leerlauf-Bewegungen macht vorerst die App selbst.

## Lernen und Gedächtnis

Gelernt wird fast nur aus Erwartungsfehlern.

- **Beziehung:** Reagiert Anna nicht auf eine Bitte, sinkt die Erwartung „reagiert auf mich“ ein
  Stück, langsam und gewichtet nach Vertrautheit.
- **Selbstbild:** Jeder Erfolg oder Misserfolg verschiebt die Kompetenzerwartung des passenden
  Bereichs. Es bleibt bei vier Bereichen.
- **Gewöhnung:** Ein Reiz, der oft ohne Folgen bleibt, verliert an Erregung.
- **Stimmung:** `Stimmung ← Stimmung + α · (Affekt − Stimmung)`. Der Affekt kehrt mit der
  Rückkehrstärke zur Grundstimmung zurück.

**Gedächtnis in drei Teilen:** Fakten („Anna mag Katzen“, auch wenn unspektakulär),
Zusagen (was, von wem, bis wann), Episoden (nur was hervorsticht, mit Affekt-Markierung).

**Takt:** Ereignisse werden sofort bewertet. Ein langsamer Takt (alle paar Sekunden) lässt
Bedürfnisse wachsen, den Affekt abklingen und die Stimmung nachziehen.

**Nachbewertung:** Nachts verdichtet ein Job die Episoden. Neu bewertet werden nur Episoden mit
hoher Relevanz, großem Erwartungsfehler *und* ungeklärtem Ausgang.

## Schnittstelle zum Sprachmodell

Das Modell bekommt keine Zahlen, sondern einen kurzen Zustandsbericht in Worten, gebaut aus Stufen
mit festen Satzbausteinen. Er ist eine einzige Zeile mit der Kennung `[Zustand]`. So gebaut seit
B1 (9. Oktober 2026), mit dem Charakter aus `charakter/reachy.toml` im Grundzustand:

```text
[Zustand] Du, LoLa, bist gut gelaunt und ruhig. Deine Art: gesellig und neugierig. Sprich freundlich und dabei ruhig und knapp, ohne Ausrufezeichen.
```

Später kommen weitere feste Bausteine dazu, zum Beispiel Tageszeit, Gegenüber und Offenes
(„Du sprichst mit Anna. Ihr seid vertraut.“). Jeder davon erst, wenn die Größe dahinter existiert.

**Sprechanweisung (entschieden nach A3, 8. Oktober 2026):** Der Bericht darf sagen, wie Reachy
sprechen soll, etwa „Sprich ruhig und knapp“. Ohne das folgt der Ton dem Zustand nur schwach
(gemessen mit Qwen3-8B). Regel: Die Sprechanweisung kommt aus derselben festen Stufentabelle in
`seele/zustandsbericht.py` wie der Zustand. Zu jeder Stufe gehört ein fester Baustein. Keine freien
Texte, keine Beispielsätze: Beispielsätze spricht das Modell nach. Der Bericht steht als eigener
Eintrag vor dem letzten Nutzersatz (`ARCHITEKTUR.md`).

Der Bericht ist eine Leitplanke, keine Garantie. Die Seele entscheidet die Handlungstendenz, das
Modell formuliert sie. Wo etwas wirklich nicht passieren darf, greift eine technische Grenze
(der Vermittler entfernt zum Beispiel Bewegungs-Tools). Über den Zustand entscheidet das Modell nie.

**Dominanz als Ausdruckswert (ab Phase 8):** Für die Haltung wird ein dritter Wert berechnet, nie
gespeichert, aus Kontrollerleben, Selbstbild und Affekt. Hoch: aufrecht, Antennen hoch.
Niedrig: geduckt, Antennen zurück. Erregung bestimmt Tempo und Ausschlag, Valenz die Grundhaltung.

## Schutzregeln

Sie gelten vor jeder Bewertung, kein Charakterwert hebt sie auf:

1. **Keine Vorwürfe an Kinder.** Ein Nähe-Defizit führt zu Einladung („Magst du mir was erzählen?“),
   nie zu Klage („Du hast mich allein gelassen“).
2. **Keine Abhängigkeit fördern.** Reachy ermutigt zu Kontakt mit anderen Menschen.
3. **Grenzen sind hart.** Motorfehler (Überhitzung, Überlast) sind Ausschlüsse.
4. **Erklärbar.** Jede Zustandsänderung steht mit ihrem Auslöser im Log.

## Was wir bewusst nicht bauen

- Dominanz als gespeicherte Achse.
- Einzelne Emotionsvariablen (Freude 0,6, Angst 0,2).
- Neuro-Simulation (Dopamin, Cortisol).
- Aus Sigma: Trauma-Faktor, Identitätskrise, Bindungsstil-Etiketten, Scham und Schuld als eigene Werte.
- Vollständiges OCC-Modell (nur Nachschlagewerk).
- Das Sprachmodell als Psyche.
- Alles speichern.

## Offene Entscheidungen

- [ ] **Autonomie als Bedürfnis?** Vorschlag: beeinflusst, *wie* Reachy etwas tut und was er danach
      bevorzugt, hebelt aber nie eine Bitte der Familie oder eine Schutzregel aus.
- [ ] **Was sagt Reachy über seine Gefühle?** Vorschlag: spricht offen über Zustände; auf direkte
      Frage sagt er ehrlich, dass er ein Roboter ist.
- [ ] **Darf sich der Charakter ändern?** Vorschlag: nein. Beziehung, Selbstbild und Erwartungen lernen.

**Prüfregel gegen Überbau:** Ab Phase 4 wird jede Zustandsgröße testweise abgeschaltet.
Ändert sich das Verhalten nicht, fliegt sie raus.

## Literatur

Dörner (1999) *Bauplan für eine Seele* · Bach (2009) *Principles of Synthetic Intelligence* ·
Ortony, Clore, Collins (1988) · Scherer (Component Process Model) · Russell (1980) ·
Kuppens u. a. (2010, DynAffect) · Frijda (1986) · Deci und Ryan (SDT) ·
Carver und Scheier (1998) · Breazeal (2002) *Designing Sociable Robots*.
