#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import time
import csv  
from multiprocessing import Process
from random import uniform

CLIENT_DATA_IP = "10.0.0.1"
SERVER_DATA_IP = "10.0.0.2"
S2C_CCA = "bbr"
FLOW_DUR = 60.0
MAX_WAIT_DUR = 5.0
NUM_FLOWS = 1000
PARALLEL = 10
BASE_PORT = 6000
NUM_CORES = 50

QUEUE_LOG = False
CLICK_ADDR = "127.0.0.1"
CLICK_PORT = 9000
UPQ = 'ohMyBtl/upq'
DOWNQ = 'ohMyBtl/downq'
HANDLER = 'length'
POLL_INTERVAL_S = 0.005

def runIperfServer(fid):
    core = fid % NUM_CORES + 1
    logfile = f"server.log.{fid}"
    port = fid + BASE_PORT
    base_params = f" -s -i 0.1 -f m -p {port} -A {core} -1"
    output_param = f" 2>&1 | tee {logfile}"
    os.system("iperf3" + base_params + output_param)

def runIperfClient(fid):
    rand_wait = round(uniform(0, MAX_WAIT_DUR), 1)
    flow_dur = FLOW_DUR - rand_wait
    core = fid % NUM_CORES + 1
    logfile = f"client.log.{fid}"
    port = fid + BASE_PORT
    base_params = (f" -i 0.1 -f m -c {CLIENT_DATA_IP} -p {port} -C {S2C_CCA} "
                   f"-A {core} -t {flow_dur} -V -P {PARALLEL}")
    output_param = f" 2>&1 | tee {logfile}"
    time.sleep(rand_wait)
    os.system("iperf3" + base_params + output_param)

def collectQueueStat(elem, csvname):
    qlen_array = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((CLICK_ADDR, CLICK_PORT))
        s.recv(1024)
        msg = ("READ %s.%s\n" % (elem, HANDLER)).encode()

        for i in range(int(DOWN_FLOW_DUR / POLL_INTERVAL_S)):
            s.send(msg)
            # The return value is three lines. Last line is the actual value.
            data = int(s.recv(1024).decode().strip().split("\n")[-1])
            qlen_array.append((i * POLL_INTERVAL_S, data))
            time.sleep(POLL_INTERVAL_S)
    with open(csvname, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['time(sec)', 'qlen'])
        writer.writerows(qlen_array)

if __name__ == "__main__":
    proc = []
    if sys.argv[1] == 'server':
        for fid in range(NUM_FLOWS//PARALLEL):
            proc.append(Process(target=runIperfServer, args=(fid,)))
    elif sys.argv[1] == 'client':
        for fid in range(NUM_FLOWS//PARALLEL):
            proc.append(Process(target=runIperfClient, args=(fid,)))
    if QUEUE_LOG:
        qstat_down = Process(target=collectQueueStat, args=(DOWNQ,'downq.csv',))
        qstat_up = Process(target=collectQueueStat, args=(UPQ,'upq.csv',))
        proc += [qstat_down, qstat_up]
    for p in proc:
        p.start()
    for p in proc:
        p.join()
