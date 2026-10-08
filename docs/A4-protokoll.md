# A4 – Protokoll (Zwischenstand 8. Oktober 2026, Sitzung beendet vor Teil 1, Schritt 3)

Nur Branch `test/a4`, wird nie gemergt. Rohdaten liegen lokal in `~/lola-laufzeit/messung/a4/`.

## Zustand am Reachy beim Abbruch – zuerst lesen
- Die Conversation App von Pollen ist **deinstalliert**. Installiert sind nur noch `feeling_machine` und
  `reachy_mini_conversation_app_local` (Jacid23).
- In der gemeinsamen Umgebung der Apps (`/venvs/apps_venv`) steht die Reachy-Bibliothek auf 1.8.0
  (vorher 1.11.0). Der Daemon selbst läuft mit 1.11.0.
- Offene Frage an Patrick: fremde App `reachy_mini_conversation_app_local` entfernen und die App von Pollen
  neu installieren (Ziel: 1.0.1, `ddc3096`)? Erst nach seinem Ja.

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
Verbindung in der App, deutsches Profil, `lola-start`/`lola-stop`, README, alle Einträge auf `entwicklung`
(ENTSCHEIDUNGEN: Versionen, Update-Befund, Log-Adresse in allen Docs korrigieren; BACKLOG: Pollen-Issue), ganz Teil 2.
