#!/bin/bash
# Usage:
#   To run a single flow from server to client, set NUM_FLOWS to 1.
#   To run a single flow from server to client with cross flow from client to
#   server, set NUM_FLOWS to 2.
#   To run two competing flows from server to client with cross flow, set
#   NUM_FLOWS to 3.
#   Then, simply execute flowgrind.sh

CLIENT_DATA_IP="10.0.0.1"
CLIENT_CTL_IP="192.168.1.101"
SERVER_DATA_IP="10.0.0.2"
SERVER_CTL_IP="192.168.1.102"
S2C_CCA="bbr"
S2C2_CCA="cubic"
C2S_CCA="cubic"
DOWN_FLOW_DUR=10.0
DOWN_FLOW2_DUR=5.0
UP_FLOW_DUR=5.0
LOGFILE="fg.log"
NUM_FLOWS=2

runFlowgrind() {
    params="-i 0.01 -n $1 -I"
    s2c_param="-F 0 -T s=$DOWN_FLOW_DUR -O s=TCP_CONGESTION=$S2C_CCA \
               -H s=$SERVER_DATA_IP/$SERVER_CTL_IP,d=$CLIENT_DATA_IP/$CLIENT_CTL_IP"
    c2s_param="-F 1 -T s=$UP_FLOW_DUR -O s=TCP_CONGESTION=$C2S_CCA -Y s=2.0 \
               -H s=$CLIENT_DATA_IP/$CLIENT_CTL_IP,d=$SERVER_DATA_IP/$SERVER_CTL_IP"
    s2c2_param="-F 2 -T s=$DOWN_FLOW2_DUR -O s=TCP_CONGESTION=$S2C2_CCA -Y s=4.0 \
                -H s=$SERVER_DATA_IP/$SERVER_CTL_IP,d=$CLIENT_DATA_IP/$CLIENT_CTL_IP"
    output_param="2>&1 | tee $LOGFILE"
    if [[ $1 -eq 3 ]]; then
        params="${params} ${s2c_param} ${c2s_param} ${s2c2_param}"
    elif [[ $1 -eq 2 ]]; then
        params="${params} ${s2c_param} ${c2s_param}"
    else
        params="${params} ${s2c_param}"
    fi
    flowgrind $params 2>&1 | tee $LOGFILE
}

runFlowgrind $NUM_FLOWS
