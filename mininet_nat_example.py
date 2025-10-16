#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


def run_nat_network():
    setLogLevel('info')

    net = Mininet()

    info("*** Creating nodes\n")
    h1 = net.addHost('h1', ip='192.168.0.1/24')
    r1 = net.addHost('r1', cls=LinuxRouter)
    s1 = net.addSwitch('s1')
    # 明示的に connect=False
    nat = net.addNAT('nat0', connect=False, ip='192.168.1.1/24')

    info("*** Creating links\n")
    net.addLink(h1, s1)
    net.addLink(r1, s1, r1_intfs=0)  # s1 側インターフェースを intf0 に固定
    net.addLink(r1, nat, r1_intfs=1)  # NAT へ直接接続

    info("*** Starting network\n")
    net.start()

    # インターフェース取得
    r1_intfs = r1.intfList()
    lan_if = r1_intfs[0]  # s1 側
    wan_if = r1_intfs[1]  # nat 側

    info(f"LAN interface: {lan_if}, WAN interface: {wan_if}\n")

    info("*** Configuring router\n")
    r1.cmd(f'ip addr add 192.168.0.254/24 dev {lan_if}')
    # NAT側と同じネットワークに設定
    r1.cmd(f'ip addr add 192.168.1.2/24 dev {wan_if}')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')

    info("*** Setting routes\n")
    h1.cmd('ip route add default via 192.168.0.254')
    r1.cmd('ip route add default via 192.168.1.1')

    info("*** NAT config\n")
    nat.configDefault()  # NAT の設定反映
    nat.cmd('ip addr add 192.168.1.1/24 dev nat0-eth0')

    info("*** Network ready. Try ping or traceroute\n")
    CLI(net)

    net.stop()


if __name__ == '__main__':
    run_nat_network()
