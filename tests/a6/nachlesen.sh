#!/bin/bash
# Zeigt, was nach einem Zeitpunkt (HH:MM:SS) in App und Sprachkette geschah: Wortlaut, Abbrüche, Zeiten, Bericht.
A=~/lola-laufzeit/lauf/app.log; S=~/lola-laufzeit/lauf/sprachkette.log
grep -v DEBUG "$A" | awk -v t="$1" '{split($2,z,","); if (z[1]>=t) print}' | grep "role=\|first audio\|Tool call\|rror\|econnect\|closed\|muted" | cut -c12-23,60-330
grep "^USER:\|^ASSISTANT:\|latency:\|JSONDecode\|disconnected\|rror" "$S" | tail -${2:-14} | sed 's/response_key.*//' | cut -c1-230
tail -${3:-3} "$(ls -t /home/moejoe/Downloads/LoLa-entwicklung/LoLa-entwicklung/daten/anfragen-*.jsonl | head -1)" | python3 -c "
import sys, json
for z in sys.stdin:
    d = json.loads(z); print('Anfrage-Log:', d.get('zeit', '')[11:19], '| gesagt:', (d.get('gesagt') or '')[:70], '| Bericht:', bool(d.get('bericht')), '| wiederholt:', d.get('wiederholt'))"
