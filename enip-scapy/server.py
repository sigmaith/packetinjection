from scapy.all import *

# Ethernet/IP 클래스 정의
class EthernetIP(Packet):
    name = "Ethernet/IP"
    fields_desc = [
        XByteField("services", 0x02),  # Register Session
        XByteField("command", 0x70),   # Send RR Data
        XShortField("length", None),   # To be filled
        StrField("session_handle", b"\x00\x00\x00\x00"),
        XShortField("status", 0x00),
        XShortField("context", 0x00),
        IntField("options", 0x00000000),
        XByteField("interface_handle", 0x00),
        XByteField("timeout", 0x0A),
        XByteField("item_count", 0x02),
        XShortField("item_length", None),  # To be filled
        XByteField("address_type", 0x00),  # Null Address
        XShortField("address_length", 0x00),  # 0 length for null address
        XShortField("address", None),  # To be filled
    ]

# 데이터를 읽는 함수 (PLC의 역할)
def read_plc_data():
    # PLC 메모리에서 읽은 값을 시뮬레이션
    plc_data = [100, 200, 300]

    # PLC 데이터를 0에서 255 범위로 클리핑
    plc_data = [max(0, min(255, x)) for x in plc_data]

    return plc_data

# Ethernet/IP 패킷 생성 및 응답
def process_eth_ip_packet(packet):
    plc_value = read_plc_data()  # PLC 데이터를 읽어옴
    plc_bytes = bytes(plc_value)  # PLC 데이터를 바이트로 변환

    response_packet = Ether() / IP(dst=packet[IP].src) / UDP() / EthernetIP(
        length=36,
        item_length=22,
        address_length=12,
        address=b"\x00\x00\x00\x00\x00\x00" + plc_bytes  # PLC 데이터 추가
    )
    sendp(response_packet, iface="Wi-Fi")

def main():
    # Ethernet/IP 특정 포트에서 패킷 수신 대기
    sniff(filter="udp and port 8000", prn=process_eth_ip_packet, iface="Wi-Fi")

if __name__ == '__main__':
    main()
