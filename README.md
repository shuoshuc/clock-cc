# Cloud gaming congestion control
This project aims to measure how each congestion control algorithm performs when supporting latency-sensitive applications (namely cloud gaming) in a residential network environment.
To this end, we emulate an asymmetric bottleneck mimicking a typical Xfinity Performance Internet plan. Since most delay-based CCAs are also subject to reverse path congestion caused by cross traffic, we run a background flow from the client to server while we study the flow of interest on the downlink (server to client).
Below we document the steps to setup such a testbed and the commands to run such experiments.

## Hardware
We use 3 machines to form a testbed, 2 of them serve as the client and server, and 1 emulates the bottleneck. The client and server each has 2 on board Intel X550 10G ports.
One port connects to the Internet and the other is used as the data plane port for testing. The bottleneck machine has 2 Intel 10G X540-AT2 ports dedicated for data plane testing.

## Topology
The testbed topology is depicted as follows.

![topology](testbed-topology.png?raw=true)

## Step 1. Install DPDK 21.11 LTS on Ubuntu 18.04.
We use [FastClick](https://github.com/tbarbette/fastclick) + [DPDK](https://www.dpdk.org/) to emulate a bottleneck with high performance and flexibility.
First, download DPDK src pack.
```
$ tar xvf dpdk-21.11.tar.xz
$ pip3 install meson ninja pyelftools
$ cd dpdk-21.11
$ meson build
$ cd build
$ ninja
$ sudo ninja install
$ sudo ldconfig
```

## Step 2. Install FastClick with DPDK support.
```
$ git clone https://github.com/tbarbette/fastclick.git
$ cd fastclick
$ ./configure --enable-dpdk --enable-intel-cpu --verbose --enable-select=poll CFLAGS="-O3" CXXFLAGS="-std=c++11 -O3"  --disable-dynamic-linking --enable-poll --enable-bound-port-transfer --enable-local --enable-flow --disable-task-stats --disable-cpu-load --enable-nanotimestamp --enable-batch --with-netmap=no --enable-zerocopy --disable-dpdk-pool --disable-dpdk-packet --enable-etherswitch
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
$ sudo modprobe uio_pci_generic
$ sudo ifconfig enp163s0f0 down
$ sudo ifconfig enp163s0f1 down
$ sudo dpdk-devbind.py --bind=uio_pci_generic enp163s0f0
$ sudo dpdk-devbind.py --bind=uio_pci_generic enp163s0f1
$ dpdk-devbind.py --status
```

## Step 5. Run FastClick on the bottleneck machine
```
$ git clone https://github.com/shuoshuc/CCA.git
$ cd CCA
$ sudo ./l2-switch.sh
```
By running l2-switch.sh, we emulate a bottleneck using the Queue + LinkUnqueue element, which dequeues packets with a fixed bandwidth and configured extra delay. This is a simple L2 learning switch running in DPDK mode.

## Step 6. Tune bottleneck parameters
To imitate a typical residential bottleneck (Xfinity Performance plan $80/mon), we set the downlink bandwidth to 100Mbps, uplink bandwidth to 10Mbps, downlink delay to 10 msec, uplink delay to 10 msec, uplink buffer size to 80 packets (MTU 1500), and downlink buffer size to 400 packets.

## Step 7. Install all CCA variants on client and server
$ sudo modprobe tcp_bbr tcp_vegas tcp_cdg tcp_lp tcp_yeah

## Step 8. Run flowgrind experiments
[Flowgrind](https://github.com/flowgrind/flowgrind) is a command line traffic generator similar to [iperf](https://iperf.fr/), but with more user control. Additionally, it has a nice centralized control, which makes running large experiments and data collection much easier. To run 1-flow, 2-flow, 3-flow experiments between lambda-1 and lambda-2, execute the following commands.
```
$ git clone https://github.com/shuoshuc/CCA.git
$ cd CCA
$ vi flowgrind.py <- update NUM_FLOWS accordingly.
$ python3 flowgrind.py
$ cat fg.log <- log is saved here.
```

## Step 9. Parse flowgrind log
With fg.log, we extract a few useful values such as throughput, cwnd, rtt. Use the fg_parser.sh to parse the log.
```
$ cd CCA
$ ./fg_parser.sh data/fg.log
```

## Step 10. Hack a CCA
To build a new CCA for study, we need to compile it as a kernel module like other CCA variants. First, install a copy of the kernel source code that matches the currently installed kernel.
```
$ sudo apt install linux-headers-$(uname -r)
```
Then build the new CCA (e.g., TCP LP2) as a module and insert it into the kernel.
```
$ cd CCA/tcp_lp2
$ sudo make
$ sudo insmod tcp_lp2.ko
```
