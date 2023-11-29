from scapy.all import *

# HTTP 패킷 필터 함수
def http_packet_filter(packet):
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        # TCP와 Raw 레이어를 가진 패킷만 필터링
        payload = packet[Raw].load.decode(errors='ignore')
        if 'HTTP' in payload:
            # HTTP 키워드를 포함하는 패킷만 필터링
            print(payload)

# 네트워크 인터페이스 설정 (여기서는 Ethernet 인터페이스를 사용하도록 설정)
iface = "Ethernet"  # 네트워크 인터페이스 이름을 실제 환경에 맞게 설정하세요

# 패킷 스니핑 시작
sniff(filter="port 80", prn=http_packet_filter, iface = "Wi-Fi")
