#! /bin/bash
#
# Simple L2 learning switch.
#
# This is a 2-port learning switch with configurable delay and rate-limiting on
# each port. Switch uses DPDK for higher performance. The config is standard
# Click configuration but only tested with FastClick.

cat << "EOF" | click --dpdk -c 0xf -n 1 --
define ($DEVNAME0 0000:a3:00.0)
define ($DEVNAME1 0000:a3:00.1)
define ($BW_Gbps 0.100000Gbps)
define ($DELAY_s 0.00)
define ($BUFFER_SIZE 128)
define ($L2TIMEOUT 3600)

in0 :: FromDPDKDevice($DEVNAME0)
in1 :: FromDPDKDevice($DEVNAME1)
out0 :: ToDPDKDevice($DEVNAME0)
out1 :: ToDPDKDevice($DEVNAME1)

elementclass Bottleneck {
  sw :: EtherSwitch(TIMEOUT $L2TIMEOUT);
  input[0], input[1]
    => [0]sw[0], [1]sw[1]
    => Queue($BUFFER_SIZE), Queue($BUFFER_SIZE)
    => LinkUnqueue($DELAY_s, $BW_Gbps), LinkUnqueue($DELAY_s, $BW_Gbps)
    => [0]output, [1]output;
}

in0, in1
  => ohMyBtl :: Bottleneck
  => out0, out1;
EOF
