from mininet.net import Mininet
from mininet.node import Controller, OVSController
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import time

def run_cloud_mqtt():
    net = Mininet(controller=OVSController, link=TCLink)
    # info('\n*** Adding controller\n')
    # net.addController('c0')

    info('\n*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    broker = net.addHost('h3', ip='10.0.0.3/24')

    info('\n*** Adding switch\n')
    s1 = net.addSwitch('s1')

    info('\n*** Creating links with 5ms delay and 10Mbps bw\n')
    net.addLink(h1, s1, bw=10, delay='5ms')
    net.addLink(h2, s1, bw=10, delay='5ms')
    net.addLink(broker, s1, bw=10, delay='5ms')

    net.start()

    info('\n*** Installing packages\n')
    for host in [h1, h2, broker]:
        host.cmd('apt-get update -y')
        host.cmd('apt-get install -y mosquitto mosquitto-clients tcpdump python3-pip')
    h1.cmd('pip install paho-mqtt')
    h2.cmd('pip install paho-mqtt')

    info('\n*** Starting MQTT Broker on broker node\n')
    broker.cmd('mosquitto -d')

    info('\n*** Starting TCPDump to capture traffic\n')
    h1.cmd('tcpdump -i h1-eth0 -w /tmp/h1.pcap &')
    h2.cmd('tcpdump -i h2-eth0 -w /tmp/h2.pcap &')
    broker.cmd('tcpdump -i h3-eth0 -w /tmp/broker.pcap &')

    info('\n*** Running MQTT test\n')
    # Subscriber script
    h2.cmd('python3 - << EOF\n'
           'import paho.mqtt.client as mqtt\n'
           'import time\n'
           'def on_message(client, userdata, msg):\n'
           '    recv_time = time.time()\n'
           '    sent_time = float(msg.payload.decode())\n'
           '    print("Latency:", recv_time - sent_time)\n'
           'client = mqtt.Client()\n'
           'client.on_message = on_message\n'
           'client.connect("10.0.0.3")\n'
           'client.subscribe("latency")\n'
           'client.loop_start()\n'
           'time.sleep(15)\n'
           'client.loop_stop()\n'
           'EOF')

    # Publisher script
    start_time = time.time()
    h1.cmd(f'python3 - << EOF\n'
           'import paho.mqtt.client as mqtt\n'
           'import time\n'
           'client = mqtt.Client()\n'
           'client.connect("10.0.0.3")\n'
           f'client.publish("latency", str({start_time}))\n'
           'EOF')

    info('\n*** Waiting a few seconds to capture all packets\n')
    time.sleep(5)

    info('\n*** Stopping TCPDump\n')
    h1.cmd('pkill tcpdump')
    h2.cmd('pkill tcpdump')
    broker.cmd('pkill tcpdump')

    info('\n*** Test complete\n')
    info('\nPCAP files: /tmp/h1.pcap, /tmp/h2.pcap, /tmp/broker.pcap\n')

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_cloud_mqtt()
