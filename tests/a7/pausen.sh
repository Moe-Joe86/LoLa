#!/usr/bin/env bash
# Vier eingeschleuste Sätze mit je 20 s Stille davor. Aufruf: pausen.sh <Name>
ZIEL=~/lola-laufzeit/messung/a7; P=~/lola-laufzeit/s2s-venv/bin/python
date +"%T Beginn $1" >> $ZIEL/ablauf.txt
for satz in "Schau bitte nach links." "Schau bitte nach rechts." "Schau bitte nach oben." "Schau bitte nach unten."; do
  sleep 20
  date +"%T.%N sage: $satz" >> $ZIEL/ablauf.txt
  $P ~/lola-laufzeit/messung/a4-pc/rpc.py conversation.say "{\"text\":\"$satz\"}" >> $ZIEL/ablauf.txt
done
sleep 5
date +"%T Ende $1" >> $ZIEL/ablauf.txt
