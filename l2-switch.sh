#! /bin/bash
#
# Simple L2 learning switch.
#
# This is a 2-port learning switch with configurable delay and rate-limiting on
# each port. Switch uses DPDK for higher performance. The config is standard
# Click configuration but only tested with FastClick.
# Config below emulates an asymmetric bottleneck:
#    uplink (port 0): 5Mbps bandwidth, 15msec delay, buffer 300 pkts (MTU1500).
#    downlink (port 1): 100Mbps bandwidth, 5msec delay, buffer 3000 pkts.

cat << "EOF" | nice -n -20 click --dpdk -c 0xff0 -n 1 --
define ($DEVNAME0 0000:a3:00.0)
define ($DEVNAME1 0000:a3:00.1)
define ($UP_BW_Gbps 0.005000Gbps)
define ($DOWN_BW_Gbps 0.100000Gbps)
define ($UP_DELAY_s 0.015)
define ($DOWN_DELAY_s 0.005)
define ($UP_BUF_SIZE 300)
define ($DOWN_BUF_SIZE 3000)
define ($L2TIMEOUT 3600)

in0 :: FromDPDKDevice($DEVNAME0)
in1 :: FromDPDKDevice($DEVNAME1)
out0 :: ToDPDKDevice($DEVNAME0)
out1 :: ToDPDKDevice($DEVNAME1)

elementclass Bottleneck {
  sw :: EtherSwitch(TIMEOUT $L2TIMEOUT);
  input[0], input[1]
    => [0]sw[0], [1]sw[1]
    => Queue($UP_BUF_SIZE), Queue($DOWN_BUF_SIZE)
    => LinkUnqueue($UP_DELAY_s, $UP_BW_Gbps), LinkUnqueue($DOWN_DELAY_s, $DOWN_BW_Gbps)
    => [0]output, [1]output;
}

in0, in1
  => ohMyBtl :: Bottleneck
  => out0, out1;
EOF
