#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import Node, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.topo import Topo

class LinuxRouter(Node):
    """ホストをルータ化するためのノードクラス"""
    def config(self, **params):
        super().config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()

class SimpleTopo(Topo):
    def build(self):
        # スイッチとNATルータを作成
        s1 = self.addSwitch('s1')
        r1 = self.addNode('r1', cls=LinuxRouter, ip='10.0.0.1/8')

        # ホスト作成
        h1 = self.addHost('h1', ip='10.0.0.10/8', defaultRoute='via 10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.11/8', defaultRoute='via 10.0.0.1')

        # リンク接続
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(s1, r1)

def run():
    setLogLevel('info')
    topo = SimpleTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
    net.start()

    r1 = net['r1']

    # r1の外側IF（ホスト共有ネットワークに接続）を有効化
    # DHCPでIPを取得
    info('*** Configuring NAT on router r1\n')
    r1.cmd('dhclient r1-eth1')  # 外部IFからDHCPでIPを取得
    r1.cmd('iptables -t nat -A POSTROUTING -o r1-eth1 -j MASQUERADE')
    r1.cmd('iptables -A FORWARD -i r1-eth0 -o r1-eth1 -j ACCEPT')
    r1.cmd('iptables -A FORWARD -i r1-eth1 -o r1-eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT')

    info('*** Network ready, test connectivity\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()
