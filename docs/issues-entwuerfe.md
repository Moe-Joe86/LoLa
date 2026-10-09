# Entwürfe für Issues bei Pollen (nicht eingereicht)

Stand 9. Oktober 2026. Vier Entwürfe, nur zum Nachlesen und späteren Einreichen durch Patrick.
Die Texte sind englisch, weil Pollens Repos englisch sind. Die Felder folgen Pollens Formular im Repo
`pollen-robotics/reachy_mini` (`.github/ISSUE_TEMPLATE/bug-report.yml`, gelesen am 9. Oktober 2026).
Das Repo der Conversation App hat kein eigenes Formular; Entwurf b benutzt dieselben Felder.

## Vor dem Einreichen

- **Logs:** Pollen verlangt Logs vollständig und unverändert („Do not shorten them, cut out the middle“).
  In den Entwürfen stehen nur die entscheidenden Zeilen als Auszug; beim Einreichen durch die vollständigen Stellen ersetzen oder die Dateien anhängen. Die ganzen Dateien liegen lokal in
  `~/lola-laufzeit/messung/` (Pfad je Entwurf genannt) und gehören als Anhang dazu. Vorher durchsehen:
  Die Logs enthalten Adressen aus dem Heimnetz und, im Log der Sprachkette, erkannte Sätze.
- **AI-Angabe:** Pollens Formular hat das Pflichtfeld „AI assistance“ mit vier Antworten. Gefunden und
  nachgestellt hat alle vier Punkte ein KI-Agent (Claude) an Patricks Roboter; Patrick hat sie bisher nicht
  selbst nachgestellt. Ehrlich ist deshalb heute:
  - reicht Patrick selbst ein, ohne nachzustellen: keine der Antworten passt genau; am nächsten ist
    „An agent filed this report, no human has reproduced it“, mit dem Satz dazu aus dem Entwurf.
  - stellt Patrick den Fehler vorher mit den Schritten selbst nach: „AI helped write this report, a human
    verified it“.
  Die Antwort „None“ wäre falsch.
- **Vor dem Einreichen prüfen**, ob es das Issue schon gibt und ob der Fehler im neuesten Stand noch besteht.
  Geprüft sind nur die unten genannten Versionen.
- Für Pull Requests gilt Pollens Regel in `CONTRIBUTING.md` der Conversation App: KI-Werkzeuge sollen keine
  PRs anlegen. Diese Entwürfe sind nur Issues.

Gemeinsame Angaben für das Formular: Robot Type **Wireless**, Operating System **Linux** (Pop!_OS, Rechner im
selben Heimnetz), Reachy Mini version **1.11.0** (Daemon auf dem Roboter, von PyPI), Troubleshooting gelesen: ja
(vor dem Einreichen wirklich lesen und ankreuzen).

---

## a) Daemon: Update einer App installiert eine andere App mit gleichem Namensanfang

**Repo:** `pollen-robotics/reachy_mini` · **Ticket Type:** 🐛 Bug Report

**Title:** App update installs a different app when two installed apps share a name prefix

**Description**

With two apps installed whose names share a prefix (`reachy_mini_conversation_app` and
`reachy_mini_conversation_app_local`), the daemon confuses them:

1. `GET /api/apps/check-updates` reports the Pollen conversation app as up to date although the installed
   revision (`a52a98a`, 0.9.0) was older than the current Space revision (`ddc3096`, 1.0.1).
2. `POST /api/apps/update/reachy_mini_conversation_app` uninstalls the Pollen app and then installs the
   *other* app (`Jacid23/reachy_mini_conversation_app_local`) with `--force-reinstall`. The job ends with
   "Successfully updated 'reachy_mini_conversation_app'". Afterwards the Pollen app is gone, and because all
   apps share `/venvs/apps_venv`, `reachy-mini` inside that venv was downgraded from 1.11.0 to 1.8.0.

Cause, from reading the code of 1.11.0: `apps/sources/app_update_checker.py`, line 73, looks up the install
info with a prefix glob:

```python
for dist_info in site_packages.glob(f"{name}*.dist-info"):
```

For `name = "reachy_mini_conversation_app"` this also matches
`reachy_mini_conversation_app_local-<version>.dist-info`, so `get_hf_install_info` can return the Space id
and revision of the other app. `AppManager.update_app` (`apps/manager.py`) then reinstalls from that Space.

**Context & Reproduction**

1. On a Wireless with daemon 1.11.0, install `pollen-robotics/reachy_mini_conversation_app` and
   `Jacid23/reachy_mini_conversation_app_local` (any second app whose name starts with the first app's name).
2. Make sure the first app is older than its Space (ours was `a52a98a`).
3. `curl http://reachy-mini.local:8000/api/apps/check-updates?force=true` → no update reported for it.
4. `curl -X POST http://reachy-mini.local:8000/api/apps/stop-current-app`
5. `curl -X POST http://reachy-mini.local:8000/api/apps/update/reachy_mini_conversation_app`
6. `curl http://reachy-mini.local:8000/api/apps/job-status/<job_id>` and
   `curl http://reachy-mini.local:8000/api/apps/list-available/installed`

Result: only the `_local` app (and other unrelated apps) are installed; the Pollen app is missing.

**Relevant logs or stack trace** (key lines of the update job, each line verbatim, lines in between left out; full job log attached)

```text
Uninstalling old version of 'reachy_mini_conversation_app'
Running command: uv pip uninstall --python /venvs/apps_venv/bin/python reachy_mini_conversation_app
 - reachy-mini-conversation-app==0.9.0 (from file:///home/pollen/.cache/huggingface/hub/spaces--pollen-robotics--reachy_mini_conversation_app/snapshots/a52a98aef4bd1527936d43414d6fbe6a9e6ced4a)
Successfully uninstalled 'reachy_mini_conversation_app'
Downloading HuggingFace Space: Jacid23/reachy_mini_conversation_app_local
Running command: uv pip install --python /venvs/apps_venv/bin/python --force-reinstall /home/pollen/.cache/huggingface/hub/spaces--Jacid23--reachy_mini_conversation_app_local/snapshots/4b9d0845313ca5a68204024a7a6b2e0bc23d53be
Successfully installed 'reachy_mini_conversation_app' in /venvs/apps_venv
Successfully updated 'reachy_mini_conversation_app'
Job 'update' completed successfully
```

From the daemon log during the same job (timestamp prefix removed):

```text
 - reachy-mini==1.11.0
 + reachy-mini==1.8.0
```

Anhang lokal: `~/lola-laufzeit/messung/a4/update-job-ergebnis.json`, `~/lola-laufzeit/messung/a4/daemon-log.txt`.

**Additional Info / Workarounds**

Removing the `_local` app (`POST /api/apps/remove/reachy_mini_conversation_app_local`) and installing the
Pollen app again (`POST /api/apps/install` with the catalog entry) gave 1.0.1. After a reboot `reachy-mini`
in `apps_venv` was back at a matching version; we assume `check_and_sync_apps_venv_sdk` did that, we did not
watch it happen. A possible fix is to match the distribution name exactly (normalised), not by prefix.

**AI assistance:** An agent filed this report, no human has reproduced it. — Zusatzsatz: "Found and
reproduced once by an AI agent (Claude) working on the reporter's robot; the reporter has read the logs
but not repeated the steps."

---

## b) Conversation App: `conversation.say` sendet aus dem Faden des `/rpc`-Servers, die Sitzung bricht ab

**Repo:** `pollen-robotics/reachy_mini_conversation_app` · **Art:** Bug

**Title:** `conversation.say` sends on the realtime websocket from the UI server thread; occasional corrupted frame drops the session

**Version:** main at `2e43e80` (also the same code in the Space revision `ddc3096`, 1.0.1); reachy-mini 1.11.0;
local backend `speech-to-speech` at `8024ccf` (`HF_REALTIME_CONNECTION_MODE=local`); app run on a Linux PC
with `--ui`, robot is a Wireless.

**Description**

Calling `conversation.say` over `/rpc` occasionally kills the realtime session. The backend receives a text
frame that is not valid JSON, closes the session, and the app reconnects about 1.4 s later. The injected
sentence is lost, and so is the conversation history of that session.

Cause, from reading the code: the `/rpc` server runs in its own thread with its own event loop
(`main.py`, `threading.Thread(target=own_ui_server.run, daemon=True, name="ui-server")`), while the realtime
connection lives in the main loop. `_rpc_say` in `console.py` awaits the handler directly:

```python
self.clear_audio_queue()  # barge in if mid-utterance
await self.handler.say(text)
```

so `conversation.item.create` and `response.create` are sent from the UI thread while the main loop keeps
sending `input_audio_buffer.append`. The personality and voice methods avoid this by hopping loops
(`personality_routes.py`, `_run_on_loop` → `asyncio.run_coroutine_threadsafe`); `say` does not.

**Context & Reproduction**

1. Run the app with `--ui` against a local `speech-to-speech` backend, microphone live.
2. Open one websocket to `ws://127.0.0.1:7860/rpc` and call
   `{"jsonrpc":"2.0","id":1,"method":"conversation.say","params":{"text":"Sag bitte nur das Wort Ja."}}`
   100 times, 0.5 s apart.
3. Count `Realtime websocket closed unexpectedly` in the app log and `JSONDecodeError` in the backend log.

Measured: 3 session drops in 100 calls at 0.5 s spacing (plus 15 calls rejected with "no active session"
during the reconnects); 2 drops in 56 calls at 4–20 s spacing. With the microphone muted around each call
(`conversation.mic` `{"muted": true}`, wait 0.1 s, `say`, unmute) there were 0 drops in 100 calls, which fits
the explanation: with the mic muted nothing else is sending.

**Relevant logs or stack trace** (excerpt, traceback shortened to the relevant frames; full logs attached)

Backend (`speech-to-speech`):

```text
2026-10-09 10:11:55,851 - [pipeline 0] speech_to_speech.api.openai_realtime.websocket_router - ERROR - Client session_8bcf430285ee42baa533ab7aa3d5198a on pipeline 0 error (JSONDecodeError): Expecting value: line 1 column 1 (char 0)
  File ".../speech_to_speech/api/openai_realtime/websocket_router.py", line 587, in realtime_endpoint
    raw = await asyncio.wait_for(ws.receive_json(), timeout=0.1)
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

App:

```text
2026-10-09 10:11:55,962 WARNING reachy_mini_conversation_app.huggingface_realtime:388 | Realtime websocket closed unexpectedly (attempt 1/3): no close frame received or sent
2026-10-09 10:11:56,013 INFO reachy_mini_conversation_app.huggingface_realtime:395 | Retrying in 1.0 seconds...
2026-10-09 10:11:57,238 INFO reachy_mini_conversation_app.huggingface_realtime:728 | Realtime session initialized with profile='lola_deutsch' voice='Aiden'
```

Anhang lokal: `~/lola-laufzeit/messung/a7/app-say.log`, `~/lola-laufzeit/messung/a7/sprachkette-say.log`
(vorher durchsehen, enthält erkannte Sätze).

**Additional Info / Workarounds**

Workaround on the caller's side: mute the mic via `conversation.mic` for the moment of the call. Normal
conversation does not seem affected: there only the main loop sends. We did not capture the corrupted frame
itself; that two threads interleave on the socket is inferred from the code and from the mute result.
Suggested fix: run `handler.say` on the handler's loop, like the personality methods do.

**AI assistance:** An agent filed this report, no human has reproduced it. — Zusatzsatz wie bei a).

---

## c) Daemon: `POST /api/audio/config/apply` lehnt Ganzzahl-Parameter ab

**Repo:** `pollen-robotics/reachy_mini` · **Ticket Type:** 🐛 Bug Report

**Title:** `/api/audio/config/apply` cannot set integer XVF3800 parameters (values are coerced to float)

**Description**

Setting an integer audio parameter over REST fails, for example `PP_NLATTENONOFF`. The request model types
all values as floats (`daemon/app/routers/audio_config.py`):

```python
class AudioParamPair(BaseModel):
    name: str
    values: list[float]
```

so `0` arrives as `0.0`, and writing an `int32` parameter (`"PP_NLATTENONOFF": (17, 27, 1, "rw", "int32")` in
`media/audio_control_utils.py`) raises "required argument is not an integer". The endpoint answers
`200 {"applied": false}`. Float parameters work. This matters for remote clients: an app running off-robot
cannot apply the audio startup config itself (no USB device) and has to go through this endpoint.

**Context & Reproduction**

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{"config":[{"name":"PP_NLATTENONOFF","values":[0]}]}' \
  http://reachy-mini.local:8000/api/audio/config/apply
# {"applied":false}

curl -X POST -H 'Content-Type: application/json' \
  -d '{"config":[{"name":"PP_MGSCALE","values":[4.0,1.0,1.0]}]}' \
  http://reachy-mini.local:8000/api/audio/config/apply
# {"applied":true}
```

**Relevant logs or stack trace** (daemon log, timestamp prefix removed)

```text
reachy_mini.media.audio_control_utils - WARNING - Failed to apply audio parameter PP_NLATTENONOFF=0.0: required argument is not an integer
reachy_mini.media.audio_control_utils - WARNING - Reachy Mini audio config completed with 1 failed parameter(s).
```

Anhang lokal: `~/lola-laufzeit/messung/a4/daemon-log-verbindung.txt`.

**Additional Info / Workarounds**

None over REST. We set the six float parameters of the conversation app's startup config and only read
`PP_NLATTENONOFF` back (`GET /api/audio/config/parameter/PP_NLATTENONOFF` works). A possible fix: accept
`list[float | int]` or convert to the parameter's declared type before writing.

**AI assistance:** An agent filed this report, no human has reproduced it. — Zusatzsatz wie bei a).

---

## d) Wunsch: Motortemperatur und Fehlerstatus über `/api/state`

**Repo:** `pollen-robotics/reachy_mini` · **Ticket Type:** 💡 Feature Request / Improvement

Nur „schöner wäre es“: Es geht heute schon über den Raw-Endpunkt.

**Title:** Expose motor temperature, hardware error status and input voltage in `/api/state`

**Description**

For an app that should notice when the robot is getting warm or a motor reports a problem, it would help to
read per motor: present temperature (register 146), hardware error status (register 70) and input voltage
(register 144). The daemon already reads registers 70 and 144 once per second in `read_hardware_errors`
(`daemon/backend/robot/backend.py`) but only writes errors to the log, so a client has to parse
`/logs/ws/daemon`. Temperature is not read at all.

**Context & Reproduction**

What works today: sending a Dynamixel protocol 2.0 read packet through `/api/move/ws/raw/write`. Example
for motor 15, register 146, one byte (robot asleep, no app running):

```text
sent:     ff ff fd 00 0f 07 00 02 92 00 01 00 3f d3
received: ff ff fd 00 0f 05 00 55 80 1b 0c 71      (27 °C)
```

All nine motors (10–18) answered, 25–33 °C. The error byte was `0x80` (alert bit) on every motor; we assume
this is the input-voltage flag that `read_hardware_errors` filters out when the voltage is fine, but we did
not read register 70 to confirm. A raw write endpoint is a heavy tool for a read-only value, and it bypasses
the daemon's own scheduling of the bus.

**Additional Info / Workarounds**

Workaround as above. A read-only field per motor in `/api/state/full` (or a small `/api/motors/health`) would
remove the need for raw packets. No urgency.

**AI assistance:** An agent filed this report, no human has reproduced it. — Zusatzsatz wie bei a).
