#! /bin/bash
#
# Simple L2 learning switch.
#
# This is a 2-port learning switch with configurable delay and rate-limiting on
# each port. Switch uses DPDK for higher performance. The config is standard
# Click configuration but only tested with FastClick.
# Config below emulates a symmetric bottleneck, client should be connected to
# port 0 and server to port 1:
#    5 Gbps bandwidth, 20msec RTT, buffer 5000 pkts (MTU1500).

+cat << "EOF" | nice -n -20 click --dpdk -l 16-31 -n 1 --
define ($DEVNAME0 0000:41:00.0)
define ($DEVNAME1 0000:41:00.1)
define ($UP_BW_Gbps 10.000000Gbps)
define ($DOWN_BW_Gbps 10.000000Gbps)
define ($UP_DELAY_s 0.010)
define ($DOWN_DELAY_s 0.010)
define ($UP_BUF_SIZE 250000)
define ($DOWN_BUF_SIZE 250000)
define ($L2TIMEOUT 3600)

ControlSocket(tcp, 9000);

in0 :: FromDPDKDevice($DEVNAME0)
in1 :: FromDPDKDevice($DEVNAME1)
out0 :: ToDPDKDevice($DEVNAME0)
out1 :: ToDPDKDevice($DEVNAME1)

elementclass Bottleneck {
  sw :: EtherSwitch(TIMEOUT $L2TIMEOUT);
  input[0], input[1]
    => [0]sw[0], [1]sw[1]
    => downq :: Queue($DOWN_BUF_SIZE), upq :: Queue($UP_BUF_SIZE)
    => LinkUnqueue($DOWN_DELAY_s, $DOWN_BW_Gbps), LinkUnqueue($UP_DELAY_s, $UP_BW_Gbps)
    => [0]output, [1]output;
}

in0, in1
  => ohMyBtl :: Bottleneck
  => out0, out1;
EOF
