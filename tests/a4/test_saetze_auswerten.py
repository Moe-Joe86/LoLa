import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("auswerten", Path(__file__).with_name("saetze_auswerten.py"))
auswerten = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auswerten)

LOG = """2026-10-09 07:28:01,552 INFO app.hf:777 | Turn latency: response.created 1 ms after user transcript
2026-10-09 07:28:01,596 INFO app.console:899 | role=user content=Lauter bitte.
2026-10-09 07:28:01,759 INFO app.huggingface_realtime:848 | Turn latency: first audio delta 208 ms after user transcript
2026-10-09 07:28:12,911 INFO app.console:899 | role=user content=Kannst du lauter machen?
2026-10-09 07:28:12,958 INFO app.huggingface_realtime:848 | Turn latency: first audio delta 81 ms after user transcript
"""


def test_lies_log_findet_saetze_und_latenzen():
    assert auswerten.lies_log(LOG) == (["Lauter bitte.", "Kannst du lauter machen?"], [208, 81])


def test_lies_log_ab_zeitpunkt():
    assert auswerten.lies_log(LOG, "07:28:10") == (["Kannst du lauter machen?"], [81])


def test_wortfehler_zaehlt_ersetzung_und_auslassung():
    soll = auswerten.woerter("Guten Morgen, LoLa.")
    assert auswerten.wortfehler(soll, auswerten.woerter("guten morgen lola")) == 0
    assert auswerten.wortfehler(soll, auswerten.woerter("Guten Morgen Lola bitte")) == 1
    assert auswerten.wortfehler(soll, auswerten.woerter("Guter Morgen")) == 2
