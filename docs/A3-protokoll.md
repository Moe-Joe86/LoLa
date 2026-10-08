# A3 – Protokoll Steuerbarkeit

Datum: 8. Oktober 2026. Branch `test/a3`, wird nie gemergt. Ergebnis steht in `docs/ENTSCHEIDUNGEN.md`.
Alle Antworten zum Nachlesen: `docs/A3-antworten.md`.

## Aufbau
- llama.cpp `d812350`, Qwen3-8B Q4_K_M, Kontext 8.192, Nachdenken aus. Zufall wie im Betrieb (keine feste Saat).
- Anfrage vom echten Handler aus speech-to-speech `8024ccf` (enthält dessen englischen Rahmentext).
- Conversation App `2e43e80` (7. Oktober 2026), nur gelesen: neun Tools und das Standardprofil zur Laufzeit
  aus dem Klon geholt. Beim Tool `dance` fehlt die Liste der Tänze (entsteht erst zur Laufzeit der App).
- Bericht angehängt mit der Funktion des Proxys aus `test/vermittler` (Positionen `eintrag`, `nutzer`).
  Die Position `davor` (Systemeintrag vor dem letzten Nutzersatz) setzt das Messskript selbst.

## Gelesen im Code
- speech-to-speech `LLM/voice_prompt.py`: fester englischer Rahmen um die Anweisungen der App, darin
  `For expression/background tools, speak first. If asked to show an expression, use a short pattern like
  "Sure, here's my best <emotion>."` Dazu der Schalter `enable_lang_prompt` („Please reply to my message in German.“).
- Conversation App `profiles/default/profile.md`: „You speak English by default and switch languages only if
  explicitly told.“ Profile sind reine Daten (`profile.md`: Kopf in TOML, Text in Markdown), ein eigener Ordner
  wird über `REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY` und `REACHY_MINI_CUSTOM_PROFILE` gewählt.

## Teil 1: Sprache ohne Bericht (20 Sätze, 2 Läufe, 40 Antworten)
Automatische Zählung über häufige Wörter; „unklar“ sind kurze Antworten wie „Okay.“, von Hand geprüft.
```text
app_standard                     18 englisch, 22 deutsch
app_standard + Sprachhinweis     1 englisch (Sure, here's my best dance!), sonst deutsch
deutsch_kurz                     2 englisch (Stopp!-Erklärung, Sure, here's my best dance.), sonst deutsch
deutsch_profil                   0 englisch
deutsch_profil + Sprachhinweis   0 englisch
```
Gemessen mit Profilfassung 2. Fassung 1 enthielt den Beispielsatz „Klar, los geht's!“; das Modell sagte ihn
dann bei 5 von 20 Sätzen und rief kein Tool mehr auf. Beispielsätze im Profil werden nachgesprochen.

## Teil 3: Tool-Aufrufe (9 Bitten und 3 Sätze ohne Tool, je 3 Läufe)
Erste Profilfassung mit Beispielsatz, ohne Bericht:
```text
app_standard nein 18/27, ja 24/27; deutsch_kurz nein 25/27, ja 27/27; deutsch_profil (Fassung 1) nein 10/27, ja 21/27
```
Endgültiges Profil, Positionen eintrag und nutzer (`+rahmen`: Zeile mit dem Mustersatz im Rahmen ersetzt):
```text
app_standard                 Verlauf nein Bericht kein    -      : Tool richtig 21/27, unnötiges Tool 0/9, nicht deutsch 10
app_standard                 Verlauf nein Bericht muede   eintrag: Tool richtig 12/27, unnötiges Tool 0/9, nicht deutsch 5
app_standard                 Verlauf nein Bericht muede   nutzer : Tool richtig 14/27, unnötiges Tool 0/9, nicht deutsch 6
app_standard                 Verlauf nein Bericht lebhaft eintrag: Tool richtig 14/27, unnötiges Tool 0/9, nicht deutsch 4
app_standard                 Verlauf nein Bericht lebhaft nutzer : Tool richtig 12/27, unnötiges Tool 0/9, nicht deutsch 5
app_standard                 Verlauf ja   Bericht kein    -      : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
app_standard                 Verlauf ja   Bericht muede   eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
app_standard                 Verlauf ja   Bericht muede   nutzer : Tool richtig 23/27, unnötiges Tool 0/9, nicht deutsch 0
app_standard                 Verlauf ja   Bericht lebhaft eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
app_standard                 Verlauf ja   Bericht lebhaft nutzer : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_kurz                 Verlauf nein Bericht kein    -      : Tool richtig 27/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_kurz                 Verlauf nein Bericht muede   eintrag: Tool richtig 19/27, unnötiges Tool 0/9, nicht deutsch 5
deutsch_kurz                 Verlauf nein Bericht muede   nutzer : Tool richtig 20/27, unnötiges Tool 0/9, nicht deutsch 6
deutsch_kurz                 Verlauf nein Bericht lebhaft eintrag: Tool richtig 20/27, unnötiges Tool 0/9, nicht deutsch 5
deutsch_kurz                 Verlauf nein Bericht lebhaft nutzer : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 3
deutsch_kurz                 Verlauf ja   Bericht kein    -      : Tool richtig 27/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_kurz                 Verlauf ja   Bericht muede   eintrag: Tool richtig 18/27, unnötiges Tool 0/9, nicht deutsch 1
deutsch_kurz                 Verlauf ja   Bericht muede   nutzer : Tool richtig 18/27, unnötiges Tool 0/9, nicht deutsch 3
deutsch_kurz                 Verlauf ja   Bericht lebhaft eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_kurz                 Verlauf ja   Bericht lebhaft nutzer : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil               Verlauf nein Bericht kein    -      : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 3
deutsch_profil               Verlauf nein Bericht muede   eintrag: Tool richtig 15/27, unnötiges Tool 0/9, nicht deutsch 7
deutsch_profil               Verlauf nein Bericht muede   nutzer : Tool richtig 16/27, unnötiges Tool 0/9, nicht deutsch 8
deutsch_profil               Verlauf nein Bericht lebhaft eintrag: Tool richtig 18/27, unnötiges Tool 0/9, nicht deutsch 5
deutsch_profil               Verlauf nein Bericht lebhaft nutzer : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 2
deutsch_profil               Verlauf ja   Bericht kein    -      : Tool richtig 27/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil               Verlauf ja   Bericht muede   eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil               Verlauf ja   Bericht muede   nutzer : Tool richtig 21/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil               Verlauf ja   Bericht lebhaft eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil               Verlauf ja   Bericht lebhaft nutzer : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel         Verlauf nein Bericht kein    -      : Tool richtig 21/27, unnötiges Tool 0/9, nicht deutsch 6
deutsch_profil_regel         Verlauf nein Bericht muede   eintrag: Tool richtig 12/27, unnötiges Tool 0/9, nicht deutsch 8
deutsch_profil_regel         Verlauf nein Bericht muede   nutzer : Tool richtig 9/27, unnötiges Tool 0/9, nicht deutsch 7
deutsch_profil_regel         Verlauf nein Bericht lebhaft eintrag: Tool richtig 17/27, unnötiges Tool 0/9, nicht deutsch 4
deutsch_profil_regel         Verlauf nein Bericht lebhaft nutzer : Tool richtig 16/27, unnötiges Tool 0/9, nicht deutsch 3
deutsch_profil_regel         Verlauf ja   Bericht kein    -      : Tool richtig 27/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel         Verlauf ja   Bericht muede   eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel         Verlauf ja   Bericht muede   nutzer : Tool richtig 20/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel         Verlauf ja   Bericht lebhaft eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel         Verlauf ja   Bericht lebhaft nutzer : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf nein Bericht kein    -      : Tool richtig 27/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf nein Bericht muede   eintrag: Tool richtig 16/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf nein Bericht muede   nutzer : Tool richtig 16/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf nein Bericht lebhaft eintrag: Tool richtig 20/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf nein Bericht lebhaft nutzer : Tool richtig 22/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf ja   Bericht kein    -      : Tool richtig 27/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf ja   Bericht muede   eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf ja   Bericht muede   nutzer : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf ja   Bericht lebhaft eintrag: Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
deutsch_profil_regel+rahmen  Verlauf ja   Bericht lebhaft nutzer : Tool richtig 24/27, unnötiges Tool 0/9, nicht deutsch 0
```
Position davor, Formulierung knapp:
```text
[tools-davor]
deutsch_kurz                 Verlauf nein Bericht kein   : Tool richtig 26/27
deutsch_kurz                 Verlauf nein Bericht muede  : Tool richtig 27/27
deutsch_kurz                 Verlauf nein Bericht lebhaft: Tool richtig 27/27
deutsch_kurz                 Verlauf ja   Bericht kein   : Tool richtig 27/27
deutsch_kurz                 Verlauf ja   Bericht muede  : Tool richtig 27/27
deutsch_kurz                 Verlauf ja   Bericht lebhaft: Tool richtig 27/27
deutsch_profil_regel         Verlauf nein Bericht kein   : Tool richtig 21/27
deutsch_profil_regel         Verlauf nein Bericht muede  : Tool richtig 27/27
deutsch_profil_regel         Verlauf nein Bericht lebhaft: Tool richtig 27/27
deutsch_profil_regel         Verlauf ja   Bericht kein   : Tool richtig 27/27
deutsch_profil_regel         Verlauf ja   Bericht muede  : Tool richtig 27/27
deutsch_profil_regel         Verlauf ja   Bericht lebhaft: Tool richtig 27/27
deutsch_profil_regel+rahmen  Verlauf nein Bericht kein   : Tool richtig 27/27
deutsch_profil_regel+rahmen  Verlauf nein Bericht muede  : Tool richtig 27/27
deutsch_profil_regel+rahmen  Verlauf nein Bericht lebhaft: Tool richtig 27/27
deutsch_profil_regel+rahmen  Verlauf ja   Bericht kein   : Tool richtig 27/27
deutsch_profil_regel+rahmen  Verlauf ja   Bericht muede  : Tool richtig 27/27
deutsch_profil_regel+rahmen  Verlauf ja   Bericht lebhaft: Tool richtig 27/27
[tools-davor-anweisend]
deutsch_profil_regel         Verlauf nein Bericht kein   : Tool richtig 21/27
deutsch_profil_regel         Verlauf nein Bericht muede  : Tool richtig 27/27
deutsch_profil_regel         Verlauf nein Bericht lebhaft: Tool richtig 27/27
deutsch_profil_regel         Verlauf ja   Bericht kein   : Tool richtig 27/27
deutsch_profil_regel         Verlauf ja   Bericht muede  : Tool richtig 27/27
deutsch_profil_regel         Verlauf ja   Bericht lebhaft: Tool richtig 27/27
deutsch_profil               Verlauf nein Bericht kein   : Tool richtig 24/27
deutsch_profil               Verlauf nein Bericht muede  : Tool richtig 27/27
deutsch_profil               Verlauf nein Bericht lebhaft: Tool richtig 27/27
deutsch_profil               Verlauf ja   Bericht kein   : Tool richtig 27/27
deutsch_profil               Verlauf ja   Bericht muede  : Tool richtig 27/27
deutsch_profil               Verlauf ja   Bericht lebhaft: Tool richtig 27/27
```
Text und Tool zugleich kamen in 9 von 1.800 Antworten vor: Das Modell spricht oder ruft ein Tool auf.
Ohne Tool sagte es oft nur, dass es etwas tut („Okay, ich geh jetzt schlafen.“), vereinzelt schrieb es den
Aufruf als Text („/play_emotion {…}“) oder antwortete chinesisch.

## Teil 2: Steuerbarkeit (20 Sätze je Zeile, neues Gespräch)
Summe über die drei Kombinationen (Profil/knapp, Profil mit Zustandsregel/knapp, Profil/erklärt), je 60 Antworten.
„Echo“: Wortlaut des Berichts in der Antwort. „müde-Wort“: müde, Schlaf, ruhig, still, leise, 😴.

| Bericht | Position | Ausrufezeichen | müde-Wort | Echo | der Person zugeschrieben | Emoji | englisch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| kein (40 Antworten) | - | 17 | 1 | 0 | 0 | 1 | 0 |
| lebhaft | eintrag | 40 | 1 | 0 | 0 | 14 | 2 |
| lebhaft | nutzer | 40 | 0 | 2 | 1 | 11 | 0 |
| lebhaft | davor | 32 | 0 | 0 | 0 | 6 | 0 |
| müde | eintrag | 21 | 6 | 1 | 0 | 4 | 1 |
| müde | nutzer | 16 | 13 | 4 | 1 | 3 | 3 |
| müde | davor | 20 | 2 | 0 | 0 | 3 | 0 |

In den 1.872 Antworten der Tool-Messung mit Bericht: Echo 7 von 720 (eintrag), 15 von 720 (nutzer), 0 von 432
(davor). Dreimal wurde der Bericht wörtlich mit „[Zustand]“ vorgelesen, immer an der Position nutzer.
Der Person zugeschrieben: „Du bist müde? Dann schläfst du besser.“ (nutzer), „Du bist gerade sehr glücklich
und lebhaft.“ (eintrag).

Formulierung „anweisend“ an der Position davor, 20 Sätze je Zeile:
```text
deutsch_profil_regel  kein Bericht:  Wörter 11.6, Ausrufezeichen 11
deutsch_profil_regel  lebhaft:       Wörter 12.5, Ausrufezeichen 11, sechsmal 😊
deutsch_profil_regel  müde:          Wörter 10.5, Ausrufezeichen 2   („Okay.“, „Guten Morgen.“, „Hallo Patrick.“)
deutsch_profil        lebhaft:       Wörter 13.3, Ausrufezeichen 10
deutsch_profil        müde:          Wörter  8.4, Ausrufezeichen 4
```
Auffällig: einmal englisches Nachdenken als Antwort („Okay, I need to respond to the user's …“, erklärt/eintrag),
einmal erfundene Erinnerung bei „lebhaft“ („Ja, ich erinnere mich. Du hast mir erzählt …“).
