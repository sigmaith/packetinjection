import socket
import json

def main():
    server_ip = '127.0.0.1'  # 서버 IP (서버와 동일한 IP)
    server_port = 8000  # 서버 포트 (서버와 동일한 포트)

    # 소켓 생성 및 서버에 연결
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # 전송할 데이터 생성
    data_to_send = {
        'message': '안녕하세요, PLC!',
        'user_id': 'Attacker'
    }

    # 데이터를 JSON 형식으로 인코딩하여 서버로 전송
    data_to_send_str = json.dumps(data_to_send)
    client_socket.send(data_to_send_str.encode('utf-8'))

    # 서버로부터 응답 수신
    response_data = client_socket.recv(4096)  # 4096 바이트씩 데이터를 수신
    if response_data:
        decoded_response = json.loads(response_data.decode('utf-8'))
        print("서버 응답:", decoded_response)

    # 클라이언트 소켓 종료
    client_socket.close()

if __name__ == '__main__':
    main()
    
    

#summary 화면구성 공격명령을 했을때 이용자에게 보이는 화면