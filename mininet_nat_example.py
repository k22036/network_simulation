#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.topo import Topo


class SingleSwitchTopo(Topo):
    "シンプルなスイッチ + 2ホストのトポロジ"

    def build(self):
        # スイッチ作成
        s1 = self.addSwitch('s1')
        # ホスト作成
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        # リンク作成
        self.addLink(h1, s1)
        self.addLink(h2, s1)


def run():
    setLogLevel('info')

    # トポロジ作成
    topo = SingleSwitchTopo()
    net = Mininet(topo=topo, switch=OVSSwitch,
                  controller=None, autoSetMacs=True)

    info('*** Adding NAT node\n')
    nat0 = net.addNAT('nat0', connect=True)  # 自動でホスト外部接続を確保
    net.start()

    # デフォルトゲートウェイ設定
    info('*** Setting default routes for hosts\n')
    for host in net.hosts:
        host.cmd('ip route add default via 10.0.0.1')

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    run()
