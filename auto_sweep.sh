#!/bin/bash

nflow="10"
for i in {1..10}
do
    python3 flowgrind.py
    mv "fg.log" "data/edge-bbr""$nflow""-run""$i"".log"
    python3 fg_parser.py log "data/edge-bbr""$nflow""-run""$i"".log"
    sleep 5
done
