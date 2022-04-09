#! /bin/bash
# Example usage:
#   ./fg_parser.sh data/bbr-cubic.log

LOGFILE=$1
CSV=(${LOGFILE//./ })
grep -Ev '^#' $LOGFILE | grep -E '^S' | awk 'BEGIN{print "flow,time,thru(Mbps),cwnd,rtt(msec)"}; { print $2","$4","$5","$13","$23 };' > $CSV".csv"
