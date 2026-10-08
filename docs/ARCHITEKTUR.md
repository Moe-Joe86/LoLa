# Architektur

Stand: 8. Oktober 2026. Quelle: Live-Dokument „Familien-Companion – Architektur & Fahrplan“
(https://claude.ai/code/artifact/e1370057-a130-448d-8bc3-b9fd9f31aa50).
Bei Widerspruch gilt diese Datei im Repo. Änderungen hier und im Live-Dokument nachziehen.

## Kurzfassung

Der Roboter wird lokal gebaut: Der Reachy Mini Wireless ist der Körper, der Linux-PC mit
NVIDIA-Grafikkarte das Gehirn. Pollens Conversation App bleibt unverändert die Stimme.
Unser eigentliches Projekt ist die **Seele**, ein eigener Dienst. Er reichert jede Anfrage
ans Sprachmodell mit Stimmung, Bedürfnissen, Beziehung und Erinnerungen an.

- **Der Hebel:** Die lokale Sprachkette von Hugging Face (speech-to-speech) ruft das
  Sprachmodell über eine HTTP-Schnittstelle auf. Dort sitzt unser Vermittler und gibt dem
  Modell bei jeder Antwort den Seelenzustand mit, ohne dass Pollen-Code geändert wird.
- **Die Psychologie** steht in `docs/KONZEPT.md`. Statt 40 paralleler Module wie in
  Unit Sigma gibt es einen einzigen Kreislauf.
- **Lokal zuerst:** Cloud-Backends sind nur eine per `.env` abschaltbare Notlösung.
  Stimmabdrücke, Gesichter und Gedächtnis verlassen nie das Heimnetz.

## Bausteine

```text
Reachy Mini Wireless                      Linux-PC (Gehirn)
┌───────────────────────────┐            ┌──────────────────────────────────────────┐
│ Stimme: Conversation App  │◄─Realtime─►│ Sprachkette (speech-to-speech)           │
│ (Pollen, unverändert)     │            │        │ Anfrage                          │
│        │ lädt             │            │        ▼                                  │
│ Werkzeuge (unser Code)    │            │ Vermittler (unser Code) ◄─Kontext─► Seele │
│                           │◄──────── conversation.say (/rpc) ─────────────── Seele │
│ Wächter (unser Code)      │            │        │ angereichert           ▲         │
│        │ /api/apps        │            │        ▼                        │         │
│ Körper: Daemon (Pollen)   │──Audio, Bild, Log───► Sinne (unser Code) ────┘         │
└───────────────────────────┘            │ Sprachmodell (llama.cpp)                 │
                                         └──────────────────────────────────────────┘
```

| Baustein | Aufgabe | läuft auf | Code |
| --- | --- | --- | --- |
| Körper (Daemon) | Motoren, Mikrofone, Kamera, Schallrichtung, App-Start | Reachy | Pollen, unverändert |
| Stimme (Conversation App) | Gesprächsschleife, Bewegung, Tool-Aufrufe | Reachy | Pollen, unverändert |
| Sprachkette (speech-to-speech) | Sprache erkennen und erzeugen | PC | Hugging Face, nur Konfiguration |
| Sprachmodell (llama.cpp) | in Worten denken | PC | nur Konfiguration |
| Vermittler | gibt jeder Anfrage den Seelenzustand mit, meldet Gesagtes zurück | PC | **unser Code** |
| Seele | Bewertung, Stimmung, Bedürfnisse, Beziehung, Gedächtnis, Eigeninitiative | PC | **unser Code** |
| Sinne | Rohdaten werden zu Wahrnehmungen: wer spricht, woher, welches Geräusch, Motorfehler | PC | **unser Code** |
| Werkzeuge und Wächter | Timer, Kalender, App-Wechsel, Rückkehr nach dem Radio | Reachy | **unser Code** |

Die Seele hängt nicht an Pollen. Ändert Pollen seine App, passen wir nur den Vermittler an.

## Wo die Seele an der App andockt

| Station im Kreislauf | was der Vermittler sieht oder tut |
| --- | --- |
| Wahrnehmung | sieht das erkannte Gesprochene. Alles andere melden die Sinne direkt an die Seele. |
| schnelle Bewertung | prüft Sprecher, Name und Wortliste, bevor die Anfrage weitergeht (Millisekunden) |
| Deutung | schickt das Gesagte parallel zur Antwort als eigenen kurzen Aufruf an dasselbe Sprachmodell |
| Verhalten | setzt den Zustandsbericht als eigenen Systemeintrag direkt vor den letzten Nutzersatz. Nur dort klappen alle Tool-Aufrufe (A3, gemessen). Vermutet, noch nicht gemessen: llama.cpp nutzt den unveränderten Anfang weiter aus dem Zwischenspeicher |
| harte Grenzen | entfernt Bewegungs-Tools aus der Anfrage, solange eine Grenze greift |
| Folge | sieht die Antwort und in der nächsten Anfrage die Ergebnisse der Tool-Aufrufe |
| Eigeninitiative | läuft nicht über den Vermittler, sondern über `conversation.say` der App |

**Tools pro Anfrage entfernen:** gegen eine Attrappe (A2) und gegen das echte llama.cpp (A1) geprüft.

## Die drei Ausgänge der Seele

1. **Kontext:** Der Vermittler legt den Zustandsbericht in jede Anfrage ans Sprachmodell,
   vor den letzten Nutzersatz. Den übrigen Systemtext reicht er unverändert durch.
2. **Sprechen:** Eigeninitiative läuft über die offizielle Steuerschnittstelle der App
   (`/rpc`, Methode `conversation.say`, im Code geprüft). Die Seele entscheidet, dass sie
   Kontakt aufnimmt, das Sprachmodell formuliert den Satz. Die Äußerung läuft durch die
   Sprachkette und bekommt so auch den Zustandsbericht.
3. **Haltung** (ab Phase 8): eine dauerhafte Körperhaltung aus der Stimmung, siehe Fahrplan.

## Geprüfte Fakten zur Conversation App (Code-Stand 7. Oktober 2026)

- Bewegung: Ein einziger Steuerpunkt (`MovementManager`). Darauf laufen nacheinander
  Emotionen, Tänze, Zielposen und ein „Atmen“ mit festen Werten (5 mm, 0,1 Hz, Antennen 15°).
- Leerlauf: Nach 180 s Stille würfelt die App lokal eine Aktion, ohne das Sprachmodell
  (60 % nichts tun, 16 % Tanz, 16 % Emotion, 8 % Kopfbewegung). Bleibt als Grundrauschen.
- `/rpc` bietet: `conversation.say`, `conversation.interrupt`, `conversation.mic`,
  `conversation.status`, `backend.config`. Erreichbar über die Web-Oberfläche auf Port 7860.
- Werkzeuge (Tools) bekommen Zugriff auf `reachy_mini` und `movement_manager`.
- Lokales Backend: `HF_REALTIME_CONNECTION_MODE=local`,
  `HF_REALTIME_WS_URL=ws://<PC-IP>:8765/v1/realtime`. Das Backend muss auf der
  Netzwerk-Adresse lauschen, nicht nur auf `127.0.0.1`.

## Körperwahrnehmung (Stand 8. Oktober 2026)

Quelle: im SDK-Code geprüft (pollen-robotics/reachy_mini, Commit `fbdbca3`: `daemon/backend/robot/backend.py` `read_hardware_errors`,
`daemon/app/routers/logs.py`, `docs/source/troubleshooting.md`). Am Roboter noch nicht geprüft, das macht A4.

- **Kein Akkustand.** Der Daemon gibt ihn nicht heraus, Pollen nennt das eine „known limitation of
  the design“; nur eine LED zeigt ihn. Müdigkeit kommt deshalb aus der Tageszeit.
- **Motorschutz:** Der Daemon prüft jede Sekunde das Fehlerregister der Motoren (Überhitzung,
  Überlast) und schreibt Fehler nur ins Log. Das Log ist lesbar über
  `ws://<reachy>:8000/api/logs/ws/daemon`. Ab Phase 4 liest `sinne/koerper.py` es und meldet eine
  Wahrnehmung. Die harte Grenze ist genau dieser Fehler.
- **Motortemperatur:** Der Daemon liest den Wert nicht von sich aus. Die Motoren (XL330) melden ihn
  aber in Register 146 (in Pollens Treiber rustypot als `present_temperature` geführt). Möglicher Weg:
  der offizielle Endpunkt `ws://<reachy>:8000/api/move/ws/raw/write`. Er gibt ein rohes Dynamixel-Paket
  über die Leitung des Daemons an den Motor und liefert die Antwort zurück. So ginge es ohne Fork und
  ohne zweiten Zugriff auf die Leitung. Ungeprüft: ob das bei laufender App sauber funktioniert (A4).
  Über diesen Weg ließen sich auch Register schreiben. Unser Code baut deshalb nur Lese-Pakete,
  ein Test sichert das ab. Rustypot selbst nutzen wir nicht: Die Leitung gehört dem Daemon.
- **IMU-Temperatur:** lesbar über `/api/state`.

## Was aus Unit Sigma übernommen wird

| Sigma | neu als | Phase |
| --- | --- | --- |
| `companion_dna`, `humor_engine` | Charakterdatei (nur Parameter) | 1 |
| `tracing` | Erklär-Log: jede Änderung mit Auslöser | 1 |
| `voice_recognition` (Sprechererkennung) | `sinne/stimme` | 3 |
| `episodic_memory`, `adaptive_memory` | `seele/gedaechtnis` (SQLite) | 3 |
| `appraisal`, `emotion_core` | `seele/bewertung`, `seele/zustand` | 4 |
| `motivation`, `needs`, `physical_self` | Bedürfnisse und Grenzen, `sinne/koerper` | 4 |
| `time_awareness`, `sleep_mode` | Wahrnehmung Tageszeit und Leerlauf | 4 |
| `relationship` | `seele/beziehung` | 5 |
| `acoustic_map` (akustische Ortung) | `sinne/richtung` | 6 |
| `classifier` (Geräusche), `speechbrain_recognizer` (Stimmlage) | `sinne/geraeusche`, `sinne/stimmlage` | 6 |
| `vision/identity_map` | `sinne/gesicht` (einfache Erkennung schon in Phase 2) | 2 / 6 |
| `decision`, `initiative`, `curiosity`, `topic_shift_manager` | Regeln in `seele/auswahl` | 7 |
| `rumination_service`, `reflection_scheduler` | nächtliche Nachbewertung | 7 |
| `narrative_generator`, `self_model`, `self_efficacy` | Lesesichten „unsere Geschichte“ und Selbstbild | 8 |
| `emotional_sway`, `speech_tapper`, `sound_library` | Körpersprache aus der Stimmung | 8 |

Nicht übernommen: eigene Audio-Pipeline (macht speech-to-speech), Diagnose-Paket,
eigenes Web-UI, Circuit-Breaker-Schicht.
