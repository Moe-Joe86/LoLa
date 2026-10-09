"""Schlägt Alarm, wenn unser Code längere Zeilen enthält, die auch in Unit Sigma stehen (CLAUDE.md, Verboten).

Sigma liegt außerhalb des Repos; der Ordner steht als `LOLA_SIGMA` in `.env` oder in der Umgebung.
Fehlt die Angabe oder der Ordner, wird der Test übersprungen. Sigma ist ein Fork der Conversation App,
der Vergleich deckt also auch Zeilen von Pollen ab.
"""

import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MINDESTLAENGE = 40  # Zeichen ohne Einrückung; kürzere Zeilen gleichen sich zufällig
UEBERGANGEN = {".venv", ".git", "__pycache__"}


def sigma_ordner() -> Path | None:
    wert = os.environ.get("LOLA_SIGMA", "")
    env_datei = REPO / ".env"
    if not wert and env_datei.exists():
        for zeile in env_datei.read_text(encoding="utf-8").splitlines():
            name, _, inhalt = zeile.partition("=")
            if name.strip() == "LOLA_SIGMA":
                wert = inhalt.strip()
    ordner = Path(wert).expanduser() if wert else None
    return ordner if ordner and ordner.is_dir() else None


def lange_zeilen(datei: Path) -> set[str]:
    """Zeilen ab der Mindestlänge, ohne Einrückung und ohne reine Import-Zeilen."""
    zeilen = (zeile.strip() for zeile in datei.read_text(encoding="utf-8", errors="replace").splitlines())
    return {z for z in zeilen if len(z) >= MINDESTLAENGE and not z.startswith(("import ", "from "))}


def python_dateien(ordner: Path) -> list[Path]:
    return [datei for datei in ordner.rglob("*.py") if not UEBERGANGEN & set(datei.relative_to(ordner).parts)]


def gleiche_zeilen(unsere: Path, fremde: Path) -> dict[str, set[str]]:
    """Je eigener Datei die langen Zeilen, die auch im fremden Ordner vorkommen."""
    fremd = set().union(*(lange_zeilen(datei) for datei in python_dateien(fremde)))
    treffer = {str(datei.relative_to(unsere)): lange_zeilen(datei) & fremd for datei in python_dateien(unsere)}
    return {name: zeilen for name, zeilen in treffer.items() if zeilen}


def test_unser_code_enthaelt_keine_langen_zeilen_aus_sigma():
    sigma = sigma_ordner()
    if sigma is None:
        pytest.skip("LOLA_SIGMA ist nicht gesetzt oder der Ordner fehlt.")
    assert gleiche_zeilen(REPO, sigma) == {}


def test_vergleich_findet_gleiche_zeile_und_uebergeht_kurze_und_importe(tmp_path):
    lang = "ergebnis = berechne_etwas_mit_vielen_worten(eingabe, schalter=True)"
    (tmp_path / "unser").mkdir()
    (tmp_path / "fremd").mkdir()
    gemeinsam = f"from irgendwo import etwas_mit_einem_sehr_langen_namen_das_gleich_ist\nx = 1\n    {lang}\n"
    (tmp_path / "unser" / "a.py").write_text(gemeinsam + "y = 2\n", encoding="utf-8")
    (tmp_path / "fremd" / "b.py").write_text(gemeinsam, encoding="utf-8")
    assert gleiche_zeilen(tmp_path / "unser", tmp_path / "fremd") == {"a.py": {lang}}
