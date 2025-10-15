#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def setup():
    net = Mininet(controller=None, link=TCLink, switch=OVSSwitch)

    info("*** Adding switch\n")
    s1 = net.addSwitch("s1", failMode="standalone")

    info("*** Adding hosts\n")
    h1 = net.addHost("h1", ip="10.0.0.10/8")
    h2 = net.addHost("h2", ip="10.0.0.11/8")

    info("*** Adding NAT router\n")
    # connect=True により自動で s1 と接続
    nat = net.addNAT(name="nat0", connect=True, inNamespace=False)

    net.addLink(h1, s1)
    net.addLink(h2, s1)

    info("*** Starting network\n")
    net.start()

    nat_ip = nat.IP()
    info(f"*** NAT IP address: {nat_ip}\n")

    info("*** Configuring default routes\n")
    ip_route_add = f"ip route add default via {nat_ip}"
    h1.cmd(ip_route_add)
    h2.cmd(ip_route_add)

    info("*** Enabling forwarding and NAT rules\n")
    nat.cmd("sysctl -w net.ipv4.ip_forward=1")
    nat.cmd("iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")

    info("*** Ready! Try 'h1 ping -c 3 8.8.8.8'\n")
    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    setup()
