#!/usr/bin/env python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink

class WordCountTopo(Topo):
    def build(self, num_clients=1):
        s1 = self.addSwitch('s1')

        # add server host
        server = self.addHost('server', ip='10.0.0.100/24')
        self.addLink(server, s1, cls=TCLink, bw=100)

        # add client hosts
        for i in range(1, num_clients + 1):
            client = self.addHost(f'c{i}', ip=f'10.0.0.{i}/24')
            self.addLink(client, s1, cls=TCLink, bw=100)

def make_net(num_clients=1):
    return Mininet(topo=WordCountTopo(num_clients=num_clients),
                   controller=OVSController,
                   autoSetMacs=True,
                   autoStaticArp=True)
