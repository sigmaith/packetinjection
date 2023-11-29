import socket
import json

def main():
    server_ip = '127.0.0.1'  # 서버 IP (클라이언트와 동일한 IP)
    server_port = 8000  # 서버 포트 (클라이언트와 동일한 포트)

    # 소켓 생성 및 바인딩
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((server_ip, server_port))
    s.listen(5)
    print(f"Server is listening on port {server_port}")

    while True:
        conn, addr = s.accept()
        print('Connection from', addr)

        # 클라이언트로부터 데이터 수신
        data = conn.recv(4096)  # 4096 바이트씩 데이터를 수신
        if not data:
            print("No more data from", addr)
            conn.close()
            break

        # 수신한 데이터 디코딩 및 처리
        received_data = json.loads(data.decode('utf-8'))
        print("Received data:", received_data)

        # 여기에 데이터 처리 로직 추가
        # 예: 데이터를 데이터베이스에 저장하거나 다른 시스템으로 전달 등

        conn.close()

if __name__ == '__main__':
    main()
    
#70~80프로 스크립트 짜기
#예제 찾기 30프로
