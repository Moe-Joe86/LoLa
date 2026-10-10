#!/bin/bash
# Startet die Kette ohne App mit einem Sprachmodell und tauscht den Vermittler gegen den Mess-Vermittler.
# Aufruf: tests/a5/kette.sh <Datei in ~/lola-laufzeit/modelle>
# Der Mess-Vermittler bleibt über `lola_start stop` hinaus laufen; am Ende von Hand beenden (pkill -f vermittler_zustand).
set -e
cd "$(dirname "$0")/../.."
uv run python -m dienste.lola_start stop > /dev/null
LOLA_SPRACHMODELL="modelle/$1" uv run python -m dienste.lola_start kette | tail -1
mkdir -p ~/lola-laufzeit/messung/a5
if [ -f ~/lola-laufzeit/lauf/vermittler.pid ]; then  # sonst läuft der Mess-Vermittler vom vorigen Modell noch
  kill -INT "$(head -1 ~/lola-laufzeit/lauf/vermittler.pid)"; rm ~/lola-laufzeit/lauf/vermittler.pid; sleep 1
  nohup uv run python tests/a5/vermittler_zustand.py > ~/lola-laufzeit/lauf/vermittler-mess.log 2>&1 &
  sleep 2
fi curl -s -m 3 -o /dev/null -w "Mess-Vermittler: %{http_code}\n" http://127.0.0.1:8091/health
nvidia-smi --query-compute-apps=name,used_memory --format=csv,noheader | grep -v cosmic
nvidia-smi --query-gpu=memory.used --format=csv,noheader
