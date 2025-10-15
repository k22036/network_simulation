import pyshark

cap = pyshark.FileCapture('/tmp/broker.pcap', display_filter='mqtt')
total_bytes = 0

for pkt in cap:
    if 'MQTT' in pkt:
        total_bytes += int(pkt.length)

print(f"Total MQTT bytes: {total_bytes}")
