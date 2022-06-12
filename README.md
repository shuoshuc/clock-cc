# Clocks and congestion control
This project aims to measure how each congestion control algorithm performs when
a globally synchronized clock is available. To this end, we emulate a bottleneck
with configurable bandwidth and latency, as well as a corresponding buffer size
as the underlying topology. Below we document the steps to setup such a testbed
and the commands to run such experiments.

## Hardware
We use 3 machines to form a testbed, 2 of them serve as the client and server,
and 1 emulates the bottleneck. The client and server each has 2 on board network
ports. One port connects to the Internet (control plane) and the other port is
used as the data plane port for experiments. The bottleneck machine, other than
its control plane port, has 2 data plane ports connecting the client and server.

## Topology
The testbed topology is depicted as follows.

![topology](testbed-topology.png?raw=true)

## Step 1. Install DPDK 19.11 LTS on Ubuntu 18.04/20.04.
We use [Click](https://github.com/kohler/click) + [DPDK](https://www.dpdk.org/)
to emulate a bottleneck with high performance and flexibility.
First, download DPDK src pack.
```
$ sudo apt install rdma-core libibverbs-dev libmnl-dev libnuma-dev
$ tar xvf dpdk-19.11.12.tar.xz
$ cd dpdk-stable-19.11.12
$ vi config/common_base
$ (Change CONFIG_RTE_EAL_IGB_UIO=n to =y if using Intel NICs, or change CONFIG_RTE_LIBRTE_MLX5_PMD=n to =y if using Mellanox CX5 NICs.)
$ make -j $(nproc) install T=x86_64-native-linuxapp-gcc
$ echo -e "export RTE_SDK=${PWD}\nexport RTE_TARGET=x86_64-native-linuxapp-gcc" >> ~/.bashrc
$ source ~/.bashrc
```

## Step 2. Install Click with DPDK support.
```
$ sudo apt install libfile-which-perl
$ git clone https://github.com/kohler/click.git
$ cd click
$ ./configure --enable-user-multithread --enable-dpdk --disable-linuxmodule --enable-intel-cpu --enable-nanotimestamp --enable-etherswitch
$ make -j $(nproc)
$ sudo make install
```

## Step 3. Reserve huge pages
```
$ sudo mkdir /mnt/huge
$ sudo mount -t hugetlbfs pagesize=1GB /mnt/huge
$ echo "nodev /mnt/huge hugetlbfs pagesize=1GB 0 0" | sudo tee -a /etc/fstab
$ sudo sed -i -r "s/GRUB_CMDLINE_LINUX=\"(.*)\"/GRUB_CMDLINE_LINUX=\"\\1 default_hugepagesz=1G hugepagesz=1G hugepages=4\"/" /etc/default/grub
$ sudo update-grub
```
Reboot the machine.

## Step 4. Bind interfaces to DPDK
```
$ sudo insmod $RTE_SDK/$RTE_TARGET/kmod/igb_uio.ko
$ sudo ifconfig enp163s0f0 down
$ sudo ifconfig enp163s0f1 down
$ sudo $RTE_SDK/usertools/dpdk-devbind.py --bind=igb_uio enp163s0f0
$ sudo $RTE_SDK/usertools/dpdk-devbind.py --bind=igb_uio enp163s0f1
$ $RTE_SDK/usertools/dpdk-devbind.py --status
```

## Step 5. Run FastClick on the bottleneck machine
```
$ git clone https://github.com/shuoshuc/clock-cc.git
$ cd clock-cc
$ sudo ./l2-switch.sh
```
By running l2-switch.sh, we emulate a bottleneck using the Queue + LinkUnqueue
element, which dequeues packets with a fixed bandwidth and configured extra
delay. This is a simple L2 learning switch running in DPDK mode.

## Step 6. Tune bottleneck parameters
To imitate a typical edge bottleneck and core ISP bottleneck, we set the
bandwidth to 100Mbps or 10Gbps, downlink/uplink delay each to 10 msec, buffer
size to 2 BDP. These parameters can be changed in l2-switch.sh.

## Step 7. Install all CCA variants on client and server
```
$ sudo modprobe tcp_bbr tcp_vegas tcp_cdg tcp_lp tcp_yeah
```

## Step 8. Run flowgrind experiments
[Flowgrind](https://github.com/flowgrind/flowgrind) is a command line traffic
generator similar to [iperf](https://iperf.fr/), but with more user control.
Additionally, it has a nice centralized control, which makes running large
experiments and data collection much easier. To run experiments with different
flows, execute the following commands.
```
$ git clone https://github.com/shuoshuc/clock-cc.git
$ cd clock-cc
$ vi flowgrind.py <- update NUM_FLOWS accordingly.
$ python3 flowgrind.py
$ cat fg.log <- log is saved here.
```

## Step 9. Parse flowgrind log
With fg.log, we extract a few useful values such as throughput, cwnd, rtt. Use
the fg_parser.sh to parse the log.
```
$ cd clock-cc
$ ./fg_parser.sh data/fg.log
```

## Step 10. Hack a CCA
To build a new CCA for study, we need to compile it as a kernel module like
other CCA variants. First, install a copy of the kernel source code that matches
the currently installed kernel.
```
$ sudo apt install linux-headers-$(uname -r)
```
Then build the new CCA (e.g., TCP LP2) as a module and insert it into the kernel.
```
$ cd CCA/tcp_lp2
$ sudo make
$ sudo insmod tcp_lp2.ko
```
