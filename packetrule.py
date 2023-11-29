import sys
from scapy.all import *

# 전역 변수로 정의된 Ethernet, IP, TCP 패킷 필드 위치
ETH_DST_MAC_POS = 0
ETH_SRC_MAC_POS = 6
ETH_TYPE_POS = 12
IP_SRC_POS = 26
IP_DST_POS = 30
TCP_SRC_PORT_POS = 34
TCP_DST_PORT_POS = 36
TCP_PAYLOAD_POS = 54

# Length of Ethernet/IP/TCP fields
ETH_DST_MAC_LEN = 6
ETH_SRC_MAC_LEN = 6
ETH_TYPE_LEN = 2
IP_SRC_LEN = 4
IP_DST_LEN = 4
TCP_SRC_PORT_LEN = 2
TCP_DST_PORT_LEN = 2

# IP fields
IP_VERSION_POS = 14
IP_HEADER_LENGTH_POS = 14
IP_TYPE_OF_SERVICE_POS = 15
IP_TOTAL_LENGTH_POS = 16
IP_IDENTIFICATION_POS = 18
IP_FRAGMENT_OFFSET_POS = 20
IP_TTL_POS = 22
IP_PROTOCOL_POS = 23
IP_CHECKSUM_POS = 24
IP_SRC_IP_POS = 26
IP_DST_IP_POS = 30

# TCP fields
TCP_SPORT_POS = 34
TCP_DPORT_POS = 36
TCP_SEQ_POS = 38
TCP_ACK_POS = 42
TCP_DATA_OFFSET_POS = 46
TCP_FLAGS_POS = 47
TCP_WINDOW_SIZE_POS = 48
TCP_CHECKSUM_POS = 50
TCP_URGENT_POINTER_POS = 52
TCP_OPTIONS_POS = 54

def parse_ethernet(packet):
    # 이더넷 헤더 파싱
    eth_header = packet[:14]

    # 필드 값 추출
    destination_mac = eth_header[ETH_DST_MAC_POS:ETH_DST_MAC_POS + ETH_DST_MAC_LEN].hex(':')
    source_mac = eth_header[ETH_SRC_MAC_POS:ETH_SRC_MAC_POS + ETH_SRC_MAC_LEN].hex()
    eth_type = eth_header[ETH_TYPE_POS:ETH_TYPE_POS + ETH_TYPE_LEN].hex()

    # 필드 값 출력
    print(f"Destination MAC: {destination_mac}")
    print(f"Source MAC: {source_mac}")
    print(f"Ethernet Type: {eth_type}")

def parse_ip(packet):
    # IP 헤더 파싱
    try:
        ip_header = packet[14:34]

        # 필드 값 추출
        version = ip_header[IP_VERSION_POS] >> 4
        header_length = (ip_header[IP_HEADER_LENGTH_POS] & 0xF) * 4
        type_of_service = ip_header[IP_TYPE_OF_SERVICE_POS]
        total_length = int.from_bytes(ip_header[IP_TOTAL_LENGTH_POS:IP_TOTAL_LENGTH_POS + 2], byteorder='big')
        identification = int.from_bytes(ip_header[IP_IDENTIFICATION_POS:IP_IDENTIFICATION_POS + 2], byteorder='big')
        fragment_offset = int.from_bytes(ip_header[IP_FRAGMENT_OFFSET_POS:IP_FRAGMENT_OFFSET_POS + 2], byteorder='big')
        ttl = ip_header[IP_TTL_POS]
        protocol = ip_header[IP_PROTOCOL_POS]
        checksum = int.from_bytes(ip_header[IP_CHECKSUM_POS:IP_CHECKSUM_POS + 2], byteorder='big')
        source_ip = socket.inet_ntoa(ip_header[IP_SRC_IP_POS:IP_SRC_IP_POS + IP_SRC_LEN])
        destination_ip = socket.inet_ntoa(ip_header[IP_DST_IP_POS:IP_DST_IP_POS + IP_DST_LEN])

        # 필드 값 출력
        print(f"Version: {version}")
        print(f"Header Length: {header_length}")
        print(f"Type of Service: {type_of_service}")
        print(f"Total Length: {total_length}")
        print(f"Identification: {identification}")
        print(f"Fragment Offset: {fragment_offset}")
        print(f"TTL: {ttl}")
        print(f"Protocol: {protocol}")
        print(f"Checksum: {checksum}")
        print(f"Source IP: {source_ip}")
        print(f"Destination IP: {destination_ip}")

    except Exception as e:
        print("Error in parse_ip:", e)

def parse_tcp(packet):
    # TCP 헤더 파싱
    tcp_header = packet[34:54]

    # 필드 값 추출
    source_port = int.from_bytes(tcp_header[TCP_SPORT_POS:TCP_SPORT_POS + TCP_SRC_PORT_LEN], byteorder='big')
    destination_port = int.from_bytes(tcp_header[TCP_DPORT_POS:TCP_DPORT_POS + TCP_DST_PORT_LEN], byteorder='big')
    sequence_number = int.from_bytes(tcp_header[TCP_SEQ_POS:TCP_SEQ_POS + 4], byteorder='big')
    acknowledgment_number = int.from_bytes(tcp_header[TCP_ACK_POS:TCP_ACK_POS + 4], byteorder='big')
    data_offset = (tcp_header[TCP_DATA_OFFSET_POS] >> 4) * 4
    control_flags = tcp_header[TCP_FLAGS_POS]
    window_size = int.from_bytes(tcp_header[TCP_WINDOW_SIZE_POS:TCP_WINDOW_SIZE_POS + 2], byteorder='big')
    checksum = int.from_bytes(tcp_header[TCP_CHECKSUM_POS:TCP_CHECKSUM_POS + 2], byteorder='big')
    urgent_pointer = int.from_bytes(tcp_header[TCP_URGENT_POINTER_POS:TCP_URGENT_POINTER_POS + 2], byteorder='big')
    options = tcp_header[TCP_OPTIONS_POS:data_offset]

    # 필드 값 출력
    print(f"Source Port: {source_port}")
    print(f"Destination Port: {destination_port}")
    print(f"Sequence Number: {sequence_number}")
    print(f"Acknowledgment Number: {acknowledgment_number}")
    print(f"Data Offset: {data_offset}")
    print("Control Flags:")
    print(f"  URG: {control_flags & 0x20 != 0}")
    print(f"  ACK: {control_flags & 0x10 != 0}")
    print(f"  PSH: {control_flags & 0x08 != 0}")
    print(f"  RST: {control_flags & 0x04 != 0}")
    print(f"  SYN: {control_flags & 0x02 != 0}")
    print(f"  FIN: {control_flags & 0x01 != 0}")
    print(f"Window Size: {window_size}")
    print(f"Checksum: {checksum}")
    print(f"Urgent Pointer: {urgent_pointer}")
    print(f"Options: {options}")

def manipulate_packet(packet):
    # Ethernet, IP, TCP 헤더 필드를 모두 0으로 조작
    packet[ETH].dst = "00:00:00:00:00:00"
    packet[ETH].src = "00:00:00:00:00:00"
    packet[IP].version = 4
    packet[IP].ihl = 5  # Header length in 32-bit words (5 words)
    packet[IP].tos = 0
    packet[IP].len = 0
    packet[IP].id = 0
    packet[IP].frag = 0
    packet[IP].ttl = 0
    packet[IP].proto = 0
    packet[IP].chksum = 0
    packet[IP].src = "0.0.0.0"
    packet[IP].dst = "0.0.0.0"
    packet[TCP].sport = 0
    packet[TCP].dport = 0

def main():
    
    if len(sys.argv) != 3:
        print("Usage: python script.py <packet_path> <field_value_data>")

    # Scapy를 사용하여 패킷 파싱
    inject_pkt = get_packet(sys.argv[1])  # 여기서는 첫 번째 패킷만 다루도록 가정
    print("Raw Packet:")
    print(inject_pkt.summary())

    # Ethernet, IP, TCP 헤더 파싱 및 출력
    parse_ethernet(bytes(inject_pkt))
    parse_ip(bytes(inject_pkt))
    parse_tcp(bytes(inject_pkt))

    #각 필드의 값 얻기
    sym_objects = get_object(sys.argv[2])

    # 패킷 조작 함수 호출
    if len(sym_objects)>0: 
    manipulate_packet(inject_pkt.data, sym_objects)

    # 조작된 패킷 출력
    print("\n조작된 패킷:")
    packet.show()

if __name__ == "__main__":
    main()


#이걸로 코드 동작 확인후
#매개변수 넘겨받는 걸로 수정

