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
- Issue bei Pollen (Repo `pollen-robotics/reachy_mini`, erst nach A4): Motortemperatur (Register 146),
  Hardware-Fehlerstatus und Eingangsspannung über `/api/state` freigeben. Der Daemon liest Register 70
  und 144 schon in `read_hardware_errors`. Dringend, falls der Raw-Endpunkt in A4 scheitert.
- Qwen3-TTS: Der Zwischenspeicher von 896 MB Grafikspeicher (`max_seq_len 4096`) ist in qwentts.cpp
  fest eingebaut. Hebel für A5: beim Projekt nachfragen oder einen Schalter vorschlagen (kein Fork).
- Anbindung an Hermes Agent für schwierige Aufträge.
- Home-Assistant-Anbindung.
- Windows-Unterstützung (zweite Priorität).
- Suche über SearXNG (selbst gehostet als Docker-Container auf der Synology, fragt u. a. DuckDuckGo
  anonym ab) statt des Such-Werkzeugs von Pollen. DuckDuckGo selbst hat keine offizielle Such-Schnittstelle.
- Ausstieg aus anderen Apps zusätzlich per Sprache („Reachy, stopp“), über das Mikrofon des Reachy auf
  dem PC. Setzt A7 voraus.
- Storyteller als eigene App in `apps/` anpassen (nur eigener Code, keine Pollen-Apps kopieren).
