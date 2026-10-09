# Backlog

Ideen für später. Nichts hiervon wird gebaut, bevor es im Fahrplan steht.
Jede Idee muss die oberste Designregel bestehen (siehe `CLAUDE.md`).

## Aus anderen Reachy-Projekten
- Morgen-Briefing: Datum, Wetter, Termine, Müllabfuhr in einem Satz (Idee aus Reachy Home Companion).
- Nachrichten an Familienmitglieder hinterlegen, Reachy überbringt sie (Reachy Home Companion).
- Einkaufsliste per Sprache (Reachy Home Companion).
- Lokaler Notfallmodus für Kernaufgaben ohne Sprachmodell (Reachy Home Companion).
- Elternzustimmung und „Recht auf Vergessen“ pro Person (ChittiOS) – bereits in Phase 3 eingeplant.
- Storyteller-Ablauf: Kind nennt Figur, Ort, Zaubergegenstand; Stimme pro Figur (Reachy Stories).

## Aus Unit Sigma
- Akustische Smileys: kurze Geräusche als Ausdruck (`sound_library`).
- Kopfbewegung im Sprechrhythmus aus der Stimmung (`emotional_sway`, `speech_tapper`).

## Technik
- Die vier Issues für Pollen liegen als Entwürfe in `docs/issues-entwuerfe.md` (Update-Prüfung, `conversation.say`,
  Ganzzahl-Parameter, Motortemperatur). Einreichen entscheidet Patrick.
- Vor der Sprechererkennung (Phase 3) prüfen: Im WebRTC-Tonstrom fehlten beim Mitlesen 3 bis 4 % der Werte,
  mit Lücken bis 210 ms (A7). Dem Daemon auf dem Reachy fehlt der Baustein `rtpgccbwe` (keine Anpassung
  der Datenrate). Hängt beides zusammen? Hat die App dieselben Lücken wie ein Mitleser?
- Issue bei Pollen (Repo `pollen-robotics/reachy_mini_conversation_app`): `conversation.say` sendet aus dem
  Faden des `/rpc`-Servers statt im Hauptfaden (`console.py`, `_rpc_say` ruft `handler.say` direkt). Folge:
  gelegentlich unlesbare Nachricht, Sitzungsabbruch. Belege in `ENTSCHEIDUNGEN.md`, 9. Oktober.
- Issue bei Pollen (Repo `pollen-robotics/reachy_mini`): `POST /api/audio/config/apply` wandelt alle Werte
  in Kommazahlen um; Ganzzahl-Parameter wie `PP_NLATTENONOFF` scheitern („required argument is not an integer“).
- Issue bei Pollen (Repo `pollen-robotics/reachy_mini`, nach A4, mit Protokollauszug): Die Update-Prüfung
  verwechselt Apps mit gleichem Namensanfang (`app_update_checker.py`, Suche `{name}*.dist-info`).
  Sie meldet „aktuell“ und installiert beim Update die falsche App. Siehe `ENTSCHEIDUNGEN.md`, 9. Oktober.
- Issue bei Pollen (Repo `pollen-robotics/reachy_mini`, erst nach A4): Motortemperatur (Register 146),
  Hardware-Fehlerstatus und Eingangsspannung über `/api/state` freigeben. Der Daemon liest Register 70
  und 144 schon in `read_hardware_errors`. Dringend, falls der Raw-Endpunkt in A4 scheitert.
- Qwen3-TTS: Der Zwischenspeicher von 896 MB Grafikspeicher (`max_seq_len 4096`) ist in qwentts.cpp
  fest eingebaut. Hebel für A5: beim Projekt nachfragen oder einen Schalter vorschlagen (kein Fork).
- Leere Zusage trotz Profil: Auf „Frau Schneider kommt heute um halb vier“ sagte das Modell „Okay, ich
  notiere das“ (B4), obwohl es nichts notieren kann. Erledigt sich mit dem Kalender in Phase 2; bis dahin
  hier geparkt. Bleibt es danach bei leeren Zusagen: Profil schärfen.
- Phase 4: gemeinsame Runden-Kennung in Erklär-Log und Anfrage-Log, dazu die Begründung der Auswahl in
  einem Satz (Idee aus Sigmas `tracing`, Steckbrief in `docs/sigma/tracing.md`). Erst bauen, wenn bei einer
  echten Fehlersuche die Zuordnung über die Uhrzeit nicht reicht.
- Kamera: Das Tool `camera` ist seit dem 9. Oktober 2026 aus dem Profil. Qwen3-8B über llama.cpp kann keine
  Bilder; die App hängt das Bild ins Gespräch, danach scheitert jede Antwort mit Fehler 500 bis zum Neustart.
  Kamera braucht ein bildfähiges Modell oder bleibt aus bis Phase 2 (Entscheidung später).
- Wann soll LoLa zuhören? Am 9. Oktober 2026 hat sie auf ein Gespräch im Raum reagiert, das nicht ihr galt.
  Später klären (Anrede, Blickrichtung, Sprechererkennung in Phase 3).
- Zwei Issue-Entwürfe für speech-to-speech in `docs/issues-entwuerfe.md` (e: Silero-Zustand wird nie
  zurückgesetzt, f: Silero setzt torch auf einen Thread). Einreichen entscheidet Patrick.
- Nächstes Mal: Sprachausgabe mit „x-vector only“ testen (`--qwen3_tts_xvec_only`). Verschwinden damit die
  stillen Überlängen (7 s und 19,5 s Ton für einen kurzen Satz, 9. Oktober 2026)?
- „Stopp!“ kam am 9. Oktober 2026 in keinem Lauf an. Für den Ausstieg per Sprache wichtig; mit Mitschnitt
  nachstellen, wenn es so weit ist.
- `dienste/sprachkette_start.py` wieder entfernen, sobald speech-to-speech die Thread-Zahl nach dem Laden
  von Silero nicht mehr auf 1 lässt (Issue-Entwurf f).
- Anbindung an Hermes Agent für schwierige Aufträge.
- Home-Assistant-Anbindung.
- Windows-Unterstützung (zweite Priorität).
- Suche über SearXNG (selbst gehostet als Docker-Container auf der Synology, fragt u. a. DuckDuckGo
  anonym ab) statt des Such-Werkzeugs von Pollen. DuckDuckGo selbst hat keine offizielle Such-Schnittstelle.
- Ausstieg aus anderen Apps zusätzlich per Sprache („Reachy, stopp“), über das Mikrofon des Reachy auf
  dem PC. Setzt A7 voraus.
- Storyteller als eigene App in `apps/` anpassen (nur eigener Code, keine Pollen-Apps kopieren).
- Start vom Reachy aus: Beim Einschalten des Reachy (oder per Geste, z. B. Antenne) startet der PC
  per Wake-on-LAN bzw. startet LoLa auf dem schon laufenden PC. Ausdrücklich kein Autostart beim
  Hochfahren des PCs (Patrick, 9. Oktober 2026). Vermutet, ungeprüft: Wake-on-LAN geht mit dem
  Z390-Board; auf dem Reachy bräuchte es dafür eine eigene kleine App in `apps/`.
