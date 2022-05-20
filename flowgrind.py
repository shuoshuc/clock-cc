#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
#   To run a single flow from server to client, set NUM_FLOWS to 1.
#   To run a single flow from server to client with cross flow from client to
#   server, set NUM_FLOWS to 2.
#   To run two competing flows from server to client with cross flow, set
#   NUM_FLOWS to 3.
#   Then, simply execute python3 flowgrind.py

import os
import socket
import time
import csv  
from multiprocessing import Process
from random import uniform

CLIENT_DATA_IP = "10.0.0.1"
CLIENT_CTL_IP = "128.105.145.240"
SERVER_DATA_IP = "10.0.0.2"
SERVER_CTL_IP = "128.105.145.242"
S2C_CCA = "bbr"
DOWN_FLOW_DUR = 30.0
MAX_WAIT_DUR = 5.0
LOGFILE = "fg.log"
NUM_FLOWS = 2

QUEUE_LOG = True
CLICK_ADDR = "127.0.0.1"
CLICK_PORT = 9000
UPQ = 'ohMyBtl/upq'
DOWNQ = 'ohMyBtl/downq'
HANDLER = 'length'
POLL_INTERVAL_S = 0.005

def runFlowgrind():
    base_params = f"-i 0.01 -n {NUM_FLOWS} -I"
    for fid in range(NUM_FLOWS):
        RAND_WAIT = uniform(0, MAX_WAIT_DUR)
        FLOW_DUR = DOWN_FLOW_DUR - RAND_WAIT
        base_params += (f" -F {fid} -Y s={RAND_WAIT} -T s={FLOW_DUR} "
                        f"-O s=TCP_CONGESTION={S2C_CCA} "
                        f"-H s={SERVER_DATA_IP}/{SERVER_CTL_IP},"
                        f"d={CLIENT_DATA_IP}/{CLIENT_CTL_IP}")
    output_param = f" 2>&1 | tee {LOGFILE}"
    os.system("flowgrind " + base_params + output_param)

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
    fg = Process(target=runFlowgrind)
    proc = [fg]
    if QUEUE_LOG:
        qstat_down = Process(target=collectQueueStat, args=(DOWNQ,'downq.csv',))
        qstat_up = Process(target=collectQueueStat, args=(UPQ,'upq.csv',))
        proc += [qstat_down, qstat_up]
    for p in proc:
        p.start()
    for p in proc:
        p.join()
