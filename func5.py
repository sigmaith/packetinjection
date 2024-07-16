import sys
from pymodbus.client import ModbusTcpClient as ModbusClient
import time

def write_single_coil_example(client, reference_number, value, file_path):
    try:
        response = client.write_coil(reference_number, value)
        # 파일 쓰기 모드를 'a'에서 'a+'로 변경하여 파일이 없는 경우 새로 생성하게 함
        with open(file_path, "a+") as file:
            if response.isError():
                file.write(f"Error writing coil at reference {reference_number}: {response}\n")
            else:
                file.write(f"Successfully wrote coil at reference {reference_number}: {value}\n")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    ip_address = '192.168.0.101'
    port = 502
    # 파일 경로 설정을 바탕화면 경로에 맞게 수정
    file_path = "C:/Users/admin/Desktop/func05_results.txt"  # Correct path

    client = ModbusClient(ip_address, port=port)
    if client.connect():
        print("Connected to the Modbus server.")
        for reference_number in range(65536):
            write_value = True
            write_single_coil_example(client, reference_number, write_value, file_path)
            time.sleep(0.01)  # Reduce speed to prevent overloading the network
    else:
        print("Failed to connect to the Modbus server.")
    client.close()

if __name__ == '__main__':
    main()
