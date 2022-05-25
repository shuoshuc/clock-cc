#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv  

def logParser(logname):
    entries = []
    csvfile = logname.split('.')[0] + '.csv'
    with open(logname, 'r') as f:
        for line in f:
            fid = -1
            chunks = line.split()
            if len(chunks) == 0:
                continue
            elif chunks[0] == 'S':
                fid = int(chunks[1])
                chunks.pop(0)
                chunks.pop(0)
            elif 'S' in chunks[0]:
                fid = int(chunks[0][1:])
                chunks.pop(0)
            else:
                continue
            ts, thru, cwnd, rtt = chunks[1], chunks[2], chunks[10], chunks[20]
            entries.append((fid, ts, thru, cwnd, rtt))
    with open(csvfile, 'w', encoding='UTF8') as outf:
        writer = csv.writer(outf)
        writer.writerow(['flow', 'time', 'thru(Mbps)', 'cwnd', 'rtt(msec)'])
        writer.writerows(entries)

if __name__ == "__main__":
    logParser(sys.argv[1])
