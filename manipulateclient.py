import socket
import binascii

def hexdump(data, width=16):
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_chunk = ' '.join([f'{b:02x}' for b in chunk])
        ascii_chunk = ''.join([chr(b) if 32 <= b < 127 else '.' for b in chunk])
        print(f'{i:04x}  {hex_chunk.ljust(width * 3)}  {ascii_chunk}')

def client():
    # 클라이언트 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # 서버에 연결
        client_socket.connect(('127.0.0.1', 8000))

        # 패킷 수신
        received_data = client_socket.recv(4096)

        print("수신된 데이터:")
        hexdump(received_data)

    finally:
        # 소켓 닫기
        client_socket.close()

if __name__ == "__main__":
    client()
