#! /bin/bash
# Example usage:
#   ./start_fgd.sh 10

NFLOWS=$1
for i in $(eval echo "{1..$NFLOWS}")
do
    flowgrindd -c $i -p $(expr 6000 + $i)
done
