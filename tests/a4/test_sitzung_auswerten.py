import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("sitzung", Path(__file__).with_name("sitzung_auswerten.py"))
sitzung = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sitzung)

LOG = """2026-10-09 13:34:12,186 - [pipeline 0] vad_handler - INFO - VAD: discarding segment=608ms active=288ms (x)
USER: Nein, danke.
2026-10-09 13:34:20,041 - [pipeline 0] notifier - INFO - Transcription completed: Nein, danke.
ASSISTANT: Kein Problem!
2026-10-09 13:34:21,055 - [pipeline 0] tts - INFO - Qwen3-TTS generated 9.01s audio in 0.34s (RTF: 8.88)
2026-10-09 13:34:21,116 - [pipeline 0] response - INFO - Turn turn_1 rev=1 latency: stt=0.54s llm=0.63s \
tts_ttfa=0.08s e2e=1.81s vad_decision=0.10s hold=0.00s smart_turn_status=incomplete status=completed
"""


def test_lies_log_sammelt_runde_verworfenes_und_ueberlange_ausgabe():
    daten = sitzung.lies_log(LOG)
    assert daten["runden"] == [
        {"zeit": "13:34:12", "erkannt": "Nein, danke.", "antwort": ["Kein Problem!"], "bis_ton_s": 1.81,
         "smart_turn": "incomplete"}
    ]
    assert daten["verworfen"] == [("13:34:12", 288)]
    assert daten["ueberlang"] == [("13:34:21", "Kein Problem!", 9.01, 0.8)]


def test_lies_log_ab_zeitpunkt_und_bericht():
    assert sitzung.lies_log(LOG, "13:35:00")["runden"] == []
    text = sitzung.bericht(sitzung.lies_log(LOG))
    assert "Antworten mit Ausrufezeichen: 1 von 1" in text
    assert "unfertig eingeschätzt: 1" in text


def test_ist_emoji():
    assert sitzung.ist_emoji("😀") and not sitzung.ist_emoji("ä")
