import socket
import sys, logging, json
from cpppo.server.enip import client
from cpppo.server.enip.getattr import attribute_operations

def read_plc_data():
    plc_ip = "192.168.1.100"  # PLC의 IP 주소
    plc_tag = ["@4/100/3"]  # PLC의 읽어올 메모리 주소 설정 (예시)

    with client.connector(
        host=plc_ip,  # PLC의 IP 주소로 변경
        port=44818,  # Ethernet/IP 표준 포트
        timeout=2.0,  # 연결 제한 시간 설정
    ) as conn:
        for index, descr, op, reply, status, value in conn.synchronous(
        operations=attribute_operations(
            plc_tag, route_path=[], send_path='' )):
                print(": %20s: %s" % (descr, value))

def write_plc_data(data_to_write):
    plc_ip = "192.168.1.100"  # PLC의 IP 주소
    plc_tag = ["@4/100/3"]  # PLC의 쓸 메모리 주소 설정 (예시)

    with client.connector(
        host=plc_ip,  # PLC의 IP 주소로 변경
        port=44818,  # Ethernet/IP 표준 포트
        timeout=2.0,  # 연결 제한 시간 설정
    ) as conn:
        write_request = conn.write(tag=plc_tag, value=data_to_write)
        response = conn.process(write_request)

        if response:
            print("PLC Digital Output 메모리에 데이터 쓰기 완료:", data_to_write)
        else:
            print("데이터 쓰기 실패")

def main():
    # PLC에서 데이터 읽어오기
    plc_data = read_plc_data()

    if plc_data is not None:
        # 데이터 수정 (임의의 값을 더하기)
        modified_data = [val + 1 for val in plc_data]

        # 수정한 데이터를 PLC에 쓰기
        write_plc_data(modified_data)

if __name__ == '__main__':
    main()
