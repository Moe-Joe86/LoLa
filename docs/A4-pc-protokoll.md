# A4-PC – Machbarkeitstest: Conversation App auf dem PC (9. Oktober 2026)

Nur Branch `test/a4-pc`, wird nie gemergt. Rohdaten lokal in `~/lola-laufzeit/messung/a4-pc/`.

## Aufbau
- App: GitHub-Stand `2e43e80`, unverändert, eigene Umgebung `~/lola-laufzeit/app-venv` (305 MB),
  Reachy-Bibliothek 1.11.0 wie der Daemon. Ohne sudo: GStreamer 1.24.2 und das WebRTC-Plugin 0.14.5 waren da.
- Start nur mit Umgebungsvariablen, keine Datei in der App: `HF_REALTIME_CONNECTION_MODE=local`,
  `HF_REALTIME_WS_URL=ws://127.0.0.1:8765/v1/realtime`, `REALTIME_TRANSCRIPTION_LANGUAGE=auto`,
  `REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY=<Repo>/tests/a4/profil`, `REACHY_MINI_CUSTOM_PROFILE=lola_deutsch`,
  `REACHY_MINI_MEMORY_ENABLED=false`, `REACHY_MINI_INSTANCE_PATH=~/lola-laufzeit/app-daten`. Aufruf mit `--ui`.
- Auf dem Reachy läuft nur der Daemon, keine App.

## Geprüft
- Die Bibliothek wählt von selbst „network“ und holt Ton und Bild per WebRTC vom Daemon.
- speech-to-speech nimmt die Sitzungs-Einstellung an („Session configuration updated“), 2.651 Token Eingabe.
- Begrüßung: „Hallo! Ich bin LoLa, und ich bin sehr froh, dich zu sehen. Wie geht es dir?“
- Tools: „Kannst du bitte nach links schauen?“ → `move_head(left)`, „Tanz bitte kurz für mich.“ → `dance`,
  beide sofort und ausgeführt (eingeschleust über `conversation.say`).
- Verbindungen der App (TCP): Reachy 8443 und 8000, Sprachkette 127.0.0.1:8765, dazu zweimal
  192.168.178.1:49000 (Router, UPnP). Keine Verbindung ins Internet gesehen.
- CPU im Leerlauf (10 s): App 55 % eines Kerns von 16, speech-to-speech 8 %, llama-server 0 %.
- Grafikspeicher: vorher 635 MiB, mit Gespräch 9.556 MiB.

## Auffällig
- „Head wobbling is only supported with the LOCAL audio backend“: Das Kopfwackeln beim Sprechen fehlt.
- „No Reachy Mini Audio USB device found“, „Reachy audio startup config was not applied“: Die App kann die
  Mikrofon-Einstellungen des Reachy von hier nicht setzen.
- Berichtigung zum Protokoll von test/a4: `Tools: []` im Log von speech-to-speech zeigt die Tool-Aufrufe
  der Antwort, nicht die angebotenen Tools. Der Befund dort (Einstellung abgelehnt) stimmt trotzdem.

## Offen
Gespräch mit Patrick, Latenz am Reachy, 20 Testsätze, Bewegungen ansehen.
