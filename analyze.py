import pyshark


def count_total_bytes(file: str) -> int:
    cap = pyshark.FileCapture(file, display_filter='mqtt')
    total_bytes = 0

    for pkt in cap:
        if 'MQTT' in pkt:
            total_bytes += int(pkt.length)
    return total_bytes


def analyze_mqtt_traffic() -> None:
    files = ['/tmp/h1.pcap', '/tmp/h2.pcap', '/tmp/broker.pcap']
    for file in files:
        total_bytes = count_total_bytes(file)
        print(f"Total MQTT bytes in {file}: {total_bytes}")


if __name__ == "__main__":
    analyze_mqtt_traffic()
