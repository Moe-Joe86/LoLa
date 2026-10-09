#!/usr/bin/env bash
# Eine Messphase: CPU-Last 30 s lang, dazu drei eingeschleuste Sätze. Aufruf: phase.sh <Name> [weitere PID]
ZIEL=~/lola-laufzeit/messung/a7; L=~/lola-laufzeit/lauf; P=~/lola-laufzeit/s2s-venv/bin/python
PIDS="$(cat $L/app.pid),$(cat $L/sprachkette.pid),$(cat $L/sprachmodell.pid)${2:+,$2}"
date +"%T Beginn $1" >> $ZIEL/ablauf.txt
curl -s -m 5 http://reachy-mini.local:8000/api/daemon/status > $ZIEL/daemon-$1-vorher.json
top -b -d 30 -n 2 -p $PIDS > $ZIEL/top-$1.txt &
for satz in "Schau bitte nach links." "Wer bist du?" "Schau bitte nach rechts."; do
  sleep 9
  date +"%T.%N sage: $satz" >> $ZIEL/ablauf.txt
  $P ~/lola-laufzeit/messung/a4-pc/rpc.py conversation.say "{\"text\":\"$satz\"}" >> $ZIEL/ablauf.txt
done
wait
curl -s -m 5 http://reachy-mini.local:8000/api/daemon/status > $ZIEL/daemon-$1-nachher.json
date +"%T Ende $1" >> $ZIEL/ablauf.txt
