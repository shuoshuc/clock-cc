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

CLIENT_DATA_IP = "10.0.0.1"
CLIENT_CTL_IP = "192.168.1.101"
SERVER_DATA_IP = "10.0.0.2"
SERVER_CTL_IP = "192.168.1.102"
S2C_CCA = "bbr"
S2C2_CCA = "cubic"
C2S_CCA = "cubic"
DOWN_FLOW_DUR = 10.0
DOWN_FLOW2_DUR = 5.0
UP_FLOW_DUR = 5.0
LOGFILE = "fg.log"
NUM_FLOWS = 2

CLICK_ADDR = "192.168.1.104"
CLICK_PORT = 9000
UPQ = 'ohMyBtl/Queue@2'
DOWNQ = 'ohMyBtl/Queue@3'
HANDLER = 'length'
POLL_INTERVAL_S = 0.005

def runFlowgrind():
    base_params = f"-i 0.01 -n {NUM_FLOWS} -I"
    s2c_param = (f" -F 0 -T s={DOWN_FLOW_DUR} -O s=TCP_CONGESTION={S2C_CCA} "
                 f"-H s={SERVER_DATA_IP}/{SERVER_CTL_IP},"
                 f"d={CLIENT_DATA_IP}/{CLIENT_CTL_IP}")
    c2s_param = (f" -F 1 -T s={UP_FLOW_DUR} -O s=TCP_CONGESTION={C2S_CCA} "
                 f"-Y s=2.0 -H s={CLIENT_DATA_IP}/{CLIENT_CTL_IP},"
                 f"d={SERVER_DATA_IP}/{SERVER_CTL_IP}")
    s2c2_param = (f" -F 2 -T s={DOWN_FLOW2_DUR} -O s=TCP_CONGESTION={S2C2_CCA} "
                  f" -Y s=4.0 -H s={SERVER_DATA_IP}/{SERVER_CTL_IP},"
                  f"d={CLIENT_DATA_IP}/{CLIENT_CTL_IP}")
    output_param = f" 2>&1 | tee {LOGFILE}"
    params = base_params + s2c_param
    if NUM_FLOWS >= 2:
        params += c2s_param
    if NUM_FLOWS >= 3:
        params += s2c2_param
    os.system("flowgrind " + params + output_param)

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
    qstat_down = Process(target=collectQueueStat, args=(DOWNQ,'downq.csv',))
    qstat_up = Process(target=collectQueueStat, args=(UPQ,'upq.csv',))
    for p in [fg, qstat_down, qstat_up]:
        p.start()
    for p in [fg, qstat_down, qstat_up]:
        p.join()
