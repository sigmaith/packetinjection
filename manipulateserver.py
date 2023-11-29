import socket
from scapy.all import rdpcap, Ether, IP, TCP, Raw

def server():
    # 서버 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8000))
    server_socket.listen(1)

    print("서버가 127.0.0.1:8000에서 연결 대기 중...")

    try:
        # 클라이언트 연결 대기
        conn, addr = server_socket.accept()
        print('클라이언트와 연결됨:', addr)

        # pcap 파일에서 첫 번째 패킷만 읽어오기
        packet = rdpcap("C:\\Users\\USER\\Downloads\\CL5000EIP-Remote-Mode-Change-Attempt.pcap")[0]

        # TCP 페이로드 수정
        original_packet = Ether(bytes(packet))
        modified_payload = b'\x00\x00' + bytes(original_packet[TCP].payload)[2:]

        # 수정된 payload를 적용한 새로운 패킷 생성
        final_pkt = IP(src=original_packet[IP].src, dst=original_packet[IP].dst) / \
                    TCP(dport=original_packet[TCP].dport, sport=original_packet[TCP].sport) / \
                    Raw(load=modified_payload)

        # 수정된 패킷을 클라이언트에게 전송
        conn.send(bytes(final_pkt))

        print("패킷을 클라이언트에게 전송했습니다.")

    finally:
        # 소켓 닫기
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    server()
