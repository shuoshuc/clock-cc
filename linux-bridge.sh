ufw disable
ifconfig enp163s0f0 promisc up
ifconfig enp163s0f1 promisc up
brctl addbr ohmybr
brctl addif ohmybr enp163s0f0 enp163s0f1
ifconfig enp163s0f0 0.0.0.0
ifconfig enp163s0f1 0.0.0.0
ifconfig ohmybr 10.0.0.100 netmask 255.255.255.0 up
