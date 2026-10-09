# A4 – Protokoll (Zwischenstand 9. Oktober 2026, vor Teil 1, Schritt 3)

Nur Branch `test/a4`, wird nie gemergt. Rohdaten liegen lokal in `~/lola-laufzeit/messung/a4/`.

## Zustand am Reachy (9. Oktober 2026, vormittags)
- Fremde App `reachy_mini_conversation_app_local` über die REST-API entfernt, `feeling_machine` bleibt.
- Conversation App von Pollen neu installiert: 1.0.1 (`ddc3096`). Geprüft an der laufenden App: 30 von 30
  Dateien der Einstellungsseite mit gleicher Prüfsumme, `/rpc` antwortet auf `conversation.status`.
- Reachy-Bibliothek in `/venvs/apps_venv`: erfüllt `>=1.10.0rc5` (uv hat sie nicht getauscht), Zeilennummern
  im Log passen zu 1.11.0. Abgeleitet, nicht abgelesen.
- Die alte `.env` der App hat überlebt: Verbindung „deployed“ (Hugging Face), Rest einer lokalen Adresse
  192.168.178.34:1234, gewähltes Profil `example` fehlt (App nimmt `default`).
- Versehen: `backend.config` ohne Angaben aufgerufen, in der Annahme, es lese nur. Es schreibt die
  Verbindung neu (gleiche Werte) und baut sie neu auf.
- App danach gestoppt, Motoren aus. Rohdaten: `daemon-log-neuinstall.txt`, `remove-job-ergebnis.json`,
  `install-job-ergebnis.json`.
- Abgleich Code 1.0.1: `say` (als Nutzer-Nachricht, bricht laufende Ausgabe ab), `interrupt`, `status`, `mic`
  vorhanden; `profile.md` wie in A3, alle 9 Tools des A3-Profils vorhanden; Profil anlegen über
  `personalities.save`/`.apply`; Werkzeug-Ordner nur per Umgebungsvariable; Leerlauf 180 s, Schlaf nach 24 h.
  Standardprofil bietet zusätzlich drei Internet-Tools (Suche, Zeit, Wetter) und `remember`/`forget`.

## Gemessen und gelesen
- Reachy: `reachy-mini.local`, 192.168.178.101, Daemon 1.11.0 (PyPI), kein stabiles Update, Vorabversion 1.12.0rc1.
- Daemon-Log: `ws://<reachy>:8000/logs/ws/daemon` (nicht `/api/logs/...`, das gibt 403).
- PC: `pop-os.local` meldet im LAN 192.168.178.123, Avahi aktiv, ufw aus. Ob der Reachy den Namen auflöst: ungeprüft.
- Sprachkette von Hand gestartet, lauscht auf 0.0.0.0:8765: llama-server 6.012 MiB, speech-to-speech 2.612 MiB,
  gesamt 9.550 MiB. Der Schalter heißt `--stream_batch_sentences 1` (nicht `--responses_api_...`).
  speech-to-speech fragt beim Start huggingface.co an (`HF_HUB_OFFLINE=1` prüfen).
- Conversation App: installiert war 0.9.0 (`a52a98a`), per Prüfsummen an der laufenden App bestätigt. Ohne `/rpc`,
  Profil als `instructions.txt`/`tools.txt`. Stand 1.0.1 (`ddc3096`) hat `/rpc` (WebSocket, Port 7860) und
  `profile.md`. Werkzeug-Ordner in beiden nur per Umgebungsvariable. Patrick hat 1.0.1 als Ziel festgelegt.
- Fehler im Daemon 1.11.0 (`apps/sources/app_update_checker.py`, Suche `{name}*.dist-info`): Für
  `reachy_mini_conversation_app` findet er die Paketdaten von `reachy_mini_conversation_app_local`. Folge:
  Die Update-Prüfung meldet fälschlich „aktuell“, und das Update installiert die fremde App statt der von Pollen.
  Beleg: `~/lola-laufzeit/messung/a4/update-job-ergebnis.json`.
- Reachy Control auf dem PC: war 0.9.19 (deb), jetzt 0.9.35 (deb von GitHub, SHA-256 geprüft). Der eingebaute
  Updater kann das deb nicht ersetzen.
- Stimmdaten: Cache `~/.cache/faster-qwen3-tts/qwentts_refs/` geleert; in `~/lola-laufzeit/stimmen/` liegen
  `frau_0.6B-Base_Q8_0` und `frau_1.7B-Base_Q8_0` (je `.spk`/`.rvq`).

## Noch nicht getan
Verbindung in der App, deutsches Profil, `lola-start`/`lola-stop`, README, ganz Teil 2.
