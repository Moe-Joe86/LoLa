import json

from vermittler.anfrage import Aenderung, bearbeite, letzter_nutzersatz, setzt_fort

BERICHT = "[Zustand] Du, LoLa, bist ruhig."


def nachricht(rolle: str, text: str) -> dict:
    art = "output_text" if rolle == "assistant" else "input_text"
    return {"type": "message", "role": rolle, "content": [{"type": art, "text": text}]}


def anfrage(**mehr) -> dict:
    eintraege = [
        nachricht("system", "Voice Rules … Du bist LoLa."),
        nachricht("user", "Hallo LoLa."),
        nachricht("assistant", "Hallo!"),
        nachricht("user", "Kannst du für mich tanzen?"),
    ]
    tools = [{"type": "function", "name": name, "parameters": {}} for name in ("dance", "move_head", "camera")]
    return {"model": "qwen3", "input": eintraege, "tools": tools, "stream": True} | mehr


def roh(koerper: dict) -> bytes:
    return json.dumps(koerper, ensure_ascii=False).encode()


def test_bericht_steht_als_eigener_systemeintrag_vor_dem_letzten_nutzersatz():
    vorher = anfrage()
    neu, aenderung = bearbeite(roh(vorher), BERICHT)
    nachher = json.loads(neu)
    assert nachher["input"][:3] == vorher["input"][:3]  # der Anfang bleibt für den Zwischenspeicher gleich
    assert nachher["input"][3] == nachricht("system", BERICHT)
    assert nachher["input"][4] == vorher["input"][3]
    assert {k: v for k, v in nachher.items() if k != "input"} == {k: v for k, v in vorher.items() if k != "input"}
    assert aenderung == Aenderung("Kannst du für mich tanzen?", BERICHT, [], stelle=3)


def test_bericht_steht_auch_nach_einem_tool_ergebnis_vor_dem_nutzersatz():
    vorher = anfrage()
    vorher["input"] += [
        {"type": "function_call", "call_id": "c1", "name": "dance", "arguments": "{}"},
        {"type": "function_call_output", "call_id": "c1", "output": "{}"},
    ]
    neu, aenderung = bearbeite(roh(vorher), BERICHT)
    assert [e.get("role", e["type"]) for e in json.loads(neu)["input"][3:]] == [
        "system", "user", "function_call", "function_call_output",
    ]
    assert aenderung.stelle == -1


def test_aufwaermen_ohne_streaming_bleibt_byte_gleich():
    aufwaermen = roh({"model": "qwen3", "input": [nachricht("system", "x"), nachricht("user", "Hello")]})
    assert bearbeite(aufwaermen, BERICHT) == (aufwaermen, Aenderung())


def test_unbekanntes_bleibt_byte_gleich():
    for koerper in (b"", b"kein json", b"[1, 2]", roh({"stream": True, "input": "nur Text"}), roh(anfrage(input=[]))):
        assert bearbeite(koerper, BERICHT) == (koerper, Aenderung())


def test_gesperrte_tools_werden_entfernt_und_gemeldet():
    neu, aenderung = bearbeite(roh(anfrage()), BERICHT, frozenset({"dance", "move_head", "gibt_es_nicht"}))
    assert [tool["name"] for tool in json.loads(neu)["tools"]] == ["camera"]
    assert aenderung.entfernte_tools == ["dance", "move_head"]


def test_ohne_bericht_und_ohne_sperre_bleibt_die_anfrage_byte_gleich():
    koerper = roh(anfrage())
    assert bearbeite(koerper, "") == (koerper, Aenderung(gesagt="Kannst du für mich tanzen?", stelle=3))


def test_umlaute_bleiben_lesbar():
    assert "für mich tanzen".encode() in bearbeite(roh(anfrage()), BERICHT)[0]


def test_letzter_nutzersatz_mit_einfachem_text_und_ohne_treffer():
    assert letzter_nutzersatz([{"role": "user", "content": "Hallo"}]) == (0, "Hallo")
    assert letzter_nutzersatz([nachricht("system", "x")]) is None


def test_setzt_fort_erkennt_dieselbe_runde_aber_nicht_den_zweimal_gesagten_satz():
    erste = Aenderung("Hi, sir, Patrick.", stelle=3)  # so in B4 gemessen: der Text ändert sich beim zweiten Anlauf
    assert setzt_fort(erste, Aenderung("Ich heiße Patrick. Wie spät ist es gerade?", stelle=3), 2.7)
    assert setzt_fort(erste, Aenderung("Hi, sir, Patrick.", stelle=3), 0.5)
    assert not setzt_fort(erste, Aenderung("Hi, sir, Patrick.", stelle=5), 2.0)  # später im Gespräch noch einmal
    assert not setzt_fort(erste, Aenderung("Hallo.", stelle=3), 60.0)  # neues Gespräch, viel später
    assert not setzt_fort(Aenderung("Tanz.", stelle=-1), Aenderung("Tanz.", stelle=-1), 0.2)  # nach Tool-Ergebnis
    assert not setzt_fort(Aenderung(), Aenderung("Tanz bitte.", stelle=1), 0.0)
