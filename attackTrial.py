from scapy.all import *
from scapy.layers.inet import IP, TCP
from scapy.all import IP, TCP, Raw
from scapy.all import conf
from scapy.all import get_if_list
import random

# Modbus/TCP 기본 설정
MODBUS_PORT = 502
TARGET_IP = '192.168.0.101'

# 취약점 찾기: 이상 동작 유발 테스트
def test_vulnerabilities():
    # 큰 패킷 생성 및 전송
    payload = bytes(RandString(size=300))  # 300바이트 무작위 데이터
    packet = IP(dst=TARGET_IP) / TCP(dport=MODBUS_PORT) / Raw(load=payload)
    send(packet)
    print("Sent large random payload packet.")

    # Source IP 스푸핑
    spoofed_packet = IP(src=TARGET_IP, dst=TARGET_IP)/TCP(sport=MODBUS_PORT, dport=MODBUS_PORT)/"Spoofed"
    send(spoofed_packet)
    print("Sent spoofed IP packet.")

# Brute Force 공격 시뮬레이션
def brute_force_attack():
    for i in range(100):  # 예를 들어 100번의 연결 시도
        try:
            response = sr1(IP(dst=TARGET_IP)/TCP(dport=MODBUS_PORT, flags="S"), timeout=1, verbose=0)
            if response and response[TCP].flags == 'SA':
                sr(IP(dst=TARGET_IP)/TCP(dport=MODBUS_PORT, flags="AR"), timeout=1, verbose=0)
                print(f"Connection {i}: Successful")
            else:
                print(f"Connection {i}: Failed")
        except Exception as e:
            print(f"Connection {i}: Exception {str(e)}")

# 패킷의 여러 계층값 변경 실험
def multi_layer_packet_modification():
    for i in range(1, 16):  # 다양한 Modbus 기능 코드
        modbus_payload = bytes(RandString(size=random.randint(10, 50)))  # 무작위 길이의 데이터
        packet = IP(dst=TARGET_IP)/TCP(dport=MODBUS_PORT)/Raw(load=modbus_payload)
        send(packet)
        print(f"Sent packet with random Modbus payload for function code {i}")

def main():
    
    print(get_if_list())

    conf.iface = "이더넷"
    test_vulnerabilities()
    brute_force_attack()
    multi_layer_packet_modification()

if __name__ == "__main__":
    main()
