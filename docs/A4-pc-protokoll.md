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

## Nachgelesen, ohne Patrick (9. Oktober 2026, vormittags)
- **Beenden:** Nach `Strg+C` an der PC-App bleiben die Motoren eingeschaltet, der Reachy steht wach.
  Von Hand über die REST-API in Schlafhaltung gelegt und Motoren ausgeschaltet (`/api/move/play/goto_sleep`,
  `/api/motors/set_mode/disabled`). Ein späteres Stopp-Skript muss das tun.
- **`2e43e80` gegen 1.0.1:** `say` (Nutzer-Nachricht), Profilformat, Leerlauf (180 s, 60/16/16/8) und Atmen
  unverändert. Neu über `/rpc`: `language.*`, `memory.*`, `vision.*`; neue Tools `robot_status`, `volume_control`.
- **Kopfwackeln:** Der Daemon hat dafür einen eigenen Schalter (`POST /api/media/wobbling/enable`), der auch
  für Ton gilt, der per WebRTC ankommt. Gelesen, nicht ausprobiert.
- **Mikrofon-Einstellungen:** Die Werte, die die App sonst setzt (`PP_AGCMAXGAIN=10`, `PP_MIN_NS=0.8` …),
  stehen am Reachy gerade so (zwei gelesen, wohl vom Lauf heute früh). Setzbar über `POST /api/audio/config/apply`.
  Ob sie einen Neustart des Reachy überleben: ungeprüft.
- **Router-Anfragen (Port 49000):** Im Code von Pollen steht nichts zu UPnP. Vermutung: die WebRTC-Bibliothek
  libnice fragt den Router von sich aus.
- **Körperdaten, nur gelesen:** IMU-Temperatur 44,25 °C (gestern im Ruhezustand 28,5 °C). In 8.692 Zeilen
  Daemon-Log von gestern und heute keine Fehlerzeile zu Motoren (Überhitzung, Überlast).
  Der Daemon meldet, dass ihm `rtpgccbwe` fehlt: keine Anpassung der Datenrate bei schlechtem Funk.
- **Vorbereitet, nicht benutzt:** `tests/a4/motortemperatur.py` (nur Lese-Pakete, Sperre und Tests; Prüfsumme
  gegen das Beispiel aus dem Robotis-Handbuch geprüft) und `tests/a4/saetze_auswerten.py` (Wortfehler und
  Latenz aus dem Log der App). `testsaetze.txt`: die 20 aus A1 plus „Guten Morgen, LoLa.“

## Zweiter Durchgang ohne Patrick (9. Oktober 2026, gegen 09 Uhr)
- **Motortemperatur gelesen** (Reachy schlafend, keine App): erst Motor 15, dann 10 bis 18: 25, 28, 26, 26, 26,
  27, 29, 31, 33 °C. Gesendet z. B. `ff ff fd 00 0f 07 00 02 92 00 01 00 3f d3`, Antwort
  `ff ff fd 00 0f 05 00 55 80 1b 0c 71`. Fehler-Byte 0x80 = Warn-Bit, bei allen Motoren. Daemon danach ohne Fehler.
- **Kopfwackeln:** Berichtigung: Die PC-App schaltet es im Daemon selbst ein und aus (Daemon-Log:
  „Head wobbler enabled (daemon-side)“). Kein eigener Schalter nötig.
- **Beenden:** Die App schläft bei Stopp absichtlich nicht (`main.py`, Kommentar bei `poll_stop_event`);
  auf dem Reachy räumt der Daemon auf (`apps/manager.py`), auf dem PC niemand.
- **Mikrofon:** `POST /api/audio/config/apply` nimmt sechs der sieben Werte; `PP_NLATTENONOFF` scheitert
  („required argument is not an integer“).
- **`lola_start` auf `entwicklung`** startet jetzt alle drei Programme und legt den Reachy beim Stoppen
  schlafen. Am Roboter geprüft: Start 22 s, Stopp 8 s, Motoren danach aus.

## Offen
Gespräch mit Patrick, Latenz am Reachy, 21 Testsätze, Bewegungen ansehen, Motortemperatur bei laufender App.
