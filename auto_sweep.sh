#!/bin/bash

nflow="200"
for i in {1..10}
do
    python3 flowgrind.py $nflow
    mv "fg.log" "data/core-bbr""$nflow""-run""$i"".log"
    sleep 5
done
mv "data/" "f200-80ms"
mkdir "data"
nflow="500"
for i in {1..10}
do
    python3 flowgrind.py $nflow
    mv "fg.log" "data/core-bbr""$nflow""-run""$i"".log"
    sleep 5
done
mv "data/" "f500-80ms"
mkdir "data"
nflow="1000"
for i in {1..10}
do
    python3 flowgrind.py $nflow
    mv "fg.log" "data/core-bbr""$nflow""-run""$i"".log"
    sleep 5
done
mv "data/" "f1000-80ms"
