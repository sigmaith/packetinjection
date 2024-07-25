import random
import time
import sys
from pymodbus.client import ModbusTcpClient as ModbusClient

# Modbus/TCP 필드 타입 정의
MODBUS_TRANSACTION_ID = "ti"
MODBUS_PROTOCOL_ID = "pi"
MODBUS_LENGTH_FIELD = "len"
MODBUS_UNIT_ID = "ui"
MODBUS_FUNCTION_CODE = "fc"
MODBUS_REFERENCE_NUMBER = "rn"


MODBUS_WRITE_DATA = "wd"
MODBUS_COUNT = "c"
MODBUS_WRITE_DATAS = "wds"
MODBUS_REGISTER_DATA = "rd"
MODBUS_REGISTER_DATAS = "rds"
MODBUS_EXCEPTION_CODE = "ec"
MODBUS_BIT_COUNT = "wc"
MODBUS_WORD_COUNT = "wc"

# Interval 
INTERVAL = "itv"

error_descriptions = {
    1: "Illegal Function: 함수 코드가 잘못되었거나, 슬레이브에서 허용되지 않음",
    2: "Illegal Data Address: 요청된 데이터 주소가 사용 가능한 주소 범위를 벗어남",
    3: "Illegal Data Value: 요청된 데이터 값이 사용 가능한 값 범위를 벗어남",
    4: "Slave Device Failure: 슬레이브 장치에서 처리할 수 없는 오류가 발생함",
    5: "Acknowledge: 요청은 받았으나, 처리하는 데 시간이 필요함",
    6: "Slave Device Busy: 슬레이브 장치가 요청을 처리할 수 없을 만큼 바쁨",
    8: "Memory Parity Error: 메모리 패리티 에러가 발생함",
    10: "Gateway Path Unavailable: 게이트웨이 경로를 사용할 수 없음",
    11: "Gateway Target Device Failed to Respond: 게이트웨이 대상 장치가 응답하지 않음"
}

def parse_input_file(file_path):
    packets = []
    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("{"):
            packet_info = line.strip("{}").strip()
            parts = packet_info.split(", ")
            packet = {} 
            for part in parts:
                key, value = part.split("=")
                value = value.strip()
                if key == INTERVAL: value = int(value)
                if key == MODBUS_FUNCTION_CODE: value = int(value)
                if key == MODBUS_REFERENCE_NUMBER: 
                    if ':' in value:
                        start, end = map(int, value.split(':'))
                        value = range(start, end+1)
                    else:
                        value = int(value)
                if key == MODBUS_WRITE_DATA: 
                    # Assuming input for wd is always "random" for function code 5
                    # and only allows 0x00 or 0xFF
                    if "random" in value:
                        options = value[value.find('(')+1:value.find(')')].split(',')
                        value = [int(option.strip(), 16) for option in options]
                    else:
                        value = int(value, 16)
                if key == MODBUS_COUNT: value = int(value)
                if key == MODBUS_WRITE_DATAS:
                    if 'random' in value:
                        count = packet[MODBUS_BIT_COUNT]
                        value = [random.choice([0x00, 0xFF]) for _ in range(count)]  
                    else:
                        value = [int(x.strip(), 16) for x in value.strip('[]').split(',')]

                if key == MODBUS_REGISTER_DATA: 
                    if "random" in value:
                        range_part = value[value.find('(')+1:value.find(")")]
                        start, end = map(lambda x: int(x,16), range_part.split(':'))
                        value = range(start, end + 1)
                    else:
                        value = int(value, 16)
                if key == MODBUS_BIT_COUNT: 
                    if "random" in value:
                        range_part = value[value.find('(')+1:value.find(")")]
                        start, end = map(lambda x: int(x,10), range_part.split(':'))
                        value = range(start, end + 1)
                    else:
                        value = int(value, 10)
                if key == MODBUS_WORD_COUNT: 
                    if "random" in value:
                        range_part = value[value.find('(')+1:value.find(")")]
                        start, end = map(lambda x: int(x,10), range_part.split(':'))
                        value = range(start, end + 1)
                    else:
                        value = int(value, 10)
                packet[key.strip()] = value
            packets.append(packet)
    return packets

def read_coils(client, packet): # func1
    try:
        reference_numbers = packet.get(MODBUS_REFERENCE_NUMBER)
        word_count = packet.get(MODBUS_WORD_COUNT)

        if not isinstance(reference_numbers, range):
            reference_numbers = [reference_numbers]

        if reference_numbers is not None and word_count is not None:
            for reference_number in reference_numbers:
                if isinstance(word_count, range):
                    actual_word_count = random.choice(list(word_count))
                else:
                    actual_word_count = word_count

                response = client.read_coils(reference_number, actual_word_count)
                if response.isError():
                    error_code = response.exception_code
                    error_message = error_descriptions.get(error_code, "알 수 없는 오류")
                    print(f"Error code: {error_code}, Error occurred: {error_message} at reference {reference_number}")
                else:
                    # 정상적인 응답 처리
                    print(f"Response data: {response} at reference {reference_number}")

    except Exception as e:
        print(f"Modbus communication error: {e}")

def read_discrete_inputs(client, packet): # func2
    try:
        reference_numbers = packet.get(MODBUS_REFERENCE_NUMBER)
        bit_count = packet.get(MODBUS_WORD_COUNT)

        if not isinstance(reference_numbers, range):
            reference_numbers = [reference_numbers]

        if reference_numbers is not None and bit_count is not None:
            for reference_number in reference_numbers:
                if isinstance(bit_count, range):
                    actual_bit_count = random.choice(list(bit_count))
                else:
                    actual_bit_count = bit_count

                response = client.read_discrete_inputs(reference_number, actual_bit_count)
                if response.isError():
                    error_code = response.exception_code
                    error_message = error_descriptions.get(error_code, "알 수 없는 오류")
                    print(f"Error code: {error_code}, Error occurred: {error_message} at reference {reference_number}")
                else:
                    # 정상적인 응답 처리
                    print(f"Response data: {response} at reference {reference_number}")

    except Exception as e:
        print(f"Modbus communication error: {e}")
    

def write_single_coil(client, packet): # func5
    try:
        reference_numbers = packet.get(MODBUS_REFERENCE_NUMBER)
        write_data = packet.get(MODBUS_WRITE_DATA)

        if not isinstance(reference_numbers, range):
            reference_numbers = [reference_numbers]

        
        for reference_number in reference_numbers:
            actual_write_data = random.choice(write_data) if isinstance(write_data, list) else write_data

            # Execute the Modbus command
            response = client.write_coil(reference_number, write_data == 0xFF)
            if response.isError():
                error_code = response.exception_code
                error_message = error_descriptions.get(error_code, "알 수 없는 오류")
                print(f"에러 코드: {error_code}, 오류 발생: {error_message} at reference {reference_number}")
            else:
                # 정상적인 응답 처리
                print(f"Successfully wrote coil at reference {reference_number}: {actual_write_data}")
    except Exception as e:
        print(f"Modbus communication error: {e}")

def write_single_register(client, packet): # func6
    try:
        reference_numbers = packet.get(MODBUS_REFERENCE_NUMBER)
        register_data = packet.get(MODBUS_REGISTER_DATA)

        if not isinstance(reference_numbers, range):
            reference_numbers = [reference_numbers]
        
        if reference_numbers is not None and register_data is not None:
            for reference_number in reference_numbers:
                if isinstance(register_data, range):
                    actual_register_data = random.choice(list(register_data))
                else:
                    actual_register_data = register_data

                response = client.write_register(reference_number, actual_register_data)
                if response.isError():
                    error_code = response.exception_code
                    error_message = error_descriptions.get(error_code, "알 수 없는 오류")
                    print(f"Error code: {error_code}, Error occurred: {error_message} at reference {reference_number}")
                else:
                    # 정상적인 응답 처리
                    print(f"Response data: {response} at reference {reference_number}")
        else:
            print("Missing reference number or register data in the packet.")
    except Exception as e:
        print(f"Modbus communication error: {e}")

def write_multiple_coils(client, packet): # func15
    try:
        reference_number = packet.get(MODBUS_REFERENCE_NUMBER)
        values = packet.get(MODBUS_WRITE_DATAS)

        if reference_number is not None and values is not None:
            # Modbus TCP 클라이언트를 사용하여 여러 코일에 값을 쓰기
            response = client.write_coils(reference_number, values)
            if response.isError():
                # 에러 처리
                print(f"Error writing coils at {reference_number}: {response}")
            else:
                # 성공 메시지 출력
                print(f"Successfully wrote coils starting at {reference_number} with values {values}")
        else:
            print("Error: Reference number or values missing")
    except Exception as e:
        print(f"Modbus communication error: {e}")

def main(argv):
    if len(argv) < 2:
        print("Usage: python script.py <path_to_file>")
        return

    file_path = argv[1]
    packets = parse_input_file(file_path)
    
    print("Parsed packets:")
    for packet in packets:
        print(packet)

    # Modbus 클라이언트 생성 및 연결
    client = ModbusClient('192.168.0.101', port=502)
    connection = client.connect()
    if not connection:
        print("Connection to Modbus server failed.")
        return

    # 패킷 처리
    for packet in packets:
        interval = packet.get(INTERVAL, 0)
        time.sleep(interval)
        function_code = packet.get(MODBUS_FUNCTION_CODE)
        if function_code == 1:
            read_coils(client, packet)
        elif function_code == 2:
            read_discrete_inputs(client, packet)
        elif function_code == 5:
            write_single_coil(client, packet)
        elif function_code == 6:
            write_single_register(client, packet)
        elif function_code == 15:
            write_multiple_coils(client, packet)

    client.close()  # 클라이언트 연결 종료

if __name__ == '__main__':
    main(sys.argv)
