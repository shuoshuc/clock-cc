#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv  
import re
import os.path
from pathlib import Path
from numpy import square, sum

def logParser(logname):
    entries, flow_map = [], {}
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
            value = flow_map.setdefault(fid, (float(ts), thru))
            if value[0] < float(ts):
                flow_map[fid] = ((float(ts), thru))
            entries.append((fid, ts, thru, cwnd, rtt))
    return (entries, flow_map)

def avgJFI(folder):
    tputs = []
    jfi = []
    pattern = re.compile(r".*D:.*through = \d+\.\d+/(\d+\.\d+) \[Mbit/s\].*")
    logs = Path(folder).glob('*.log')
    for log in logs:
        col = str(log.stem).split('-')[1][3:]
        with open(log, 'r') as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    tputs.append(float(match.group(1)))
        jfi.append([square(sum(tputs)) / (len(tputs) * sum(square(tputs)))])
    with open(os.path.join(folder, 'jfi.csv'), 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow([f'f{col}'])
        writer.writerows(jfi)

def finalJFI(folder):
    tputs = []
    jfi = []
    pattern = re.compile(r".*D:.*through = \d+\.\d+/(\d+\.\d+) \[Mbit/s\].*")
    logs = Path(folder).glob('*.log')
    for log in logs:
        (_, flow_map) = logParser(log)
        col = str(log.stem).split('-')[1][3:]
        for flow in flow_map.values():
            tputs.append(float(flow[1]))
        jfi.append([square(sum(tputs)) / (len(tputs) * sum(square(tputs)))])
    with open(os.path.join(folder, 'jfi.csv'), 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow([f'f{col}'])
        writer.writerows(jfi)

def waitThru(folder):
    wait_tputs = []
    pattern = re.compile(r"^# ID[ ]+(\d+).*D:.*read delay = (\d+\.\d+).*through")
    logname_pattern = re.compile(r".*run(\d+)\.log")
    logs = Path(folder).glob('*.log')
    for log in logs:
        log_match = logname_pattern.match(str(log))
        if log_match:
            run = log_match.group(1)
        (_, flow_map) = logParser(log)
        with open(log, 'r') as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    wait_tputs.append((run, match.group(1),
                                       float(match.group(2)),
                                       flow_map[int(match.group(1))][1]))
    with open(os.path.join(folder, 'wait_tput.csv'), 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow(['run', 'flow', 'wait(sec)', 'thru(Mbps)'])
        writer.writerows(wait_tputs)

def kernLog(logfile):
    entries = []
    pattern = re.compile(r".*\[(.*) PROBE_RTT\] sk=(.*) at (\d+), min_rtt_us=(\d+)")
    with open(logfile, 'r') as f:
        for line in f:
            match = pattern.match(line)
            if match:
                entries.append((match.group(1), match.group(2), match.group(3), match.group(4)))
    csvfile = logfile.split('.')[0] + '.csv'
    with open(csvfile, 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow(['state', 'sk', 'ts(ns)', 'minrtt(us)'])
        writer.writerows(entries)

if __name__ == "__main__":
    if sys.argv[1] == 'log':
        logs = Path(sys.argv[2]).glob('*.log')
        for log in logs:
            (entries, _) = logParser(log)
            csvfile = str(log).split('.')[0] + '.csv'
            with open(csvfile, 'w', encoding='UTF8') as outf:
                writer = csv.writer(outf)
                writer.writerow(['flow', 'time', 'thru(Mbps)', 'cwnd',
                                 'rtt(msec)'])
                writer.writerows(entries)
    elif sys.argv[1] == 'jfi':
        #avgJFI(sys.argv[2])
        finalJFI(sys.argv[2])
    elif sys.argv[1] == 'wait':
        waitThru(sys.argv[2])
    elif sys.argv[1] == 'kern':
        kernLog(sys.argv[2])
