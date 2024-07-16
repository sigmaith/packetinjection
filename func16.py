import sys
from pymodbus.client import ModbusTcpClient as ModbusClient
import time
import random

def write_multiple_registers_example(client, starting_address, values, file_path):
    try:
        response = client.write_registers(starting_address, values)
        with open(file_path, "a+") as file:
            if response.isError():
                error_code = response.exception_code
                file.write(f"Error writing registers starting at {starting_address}: {error_code}\n")
            else:
                file.write(f"Successfully wrote registers starting at {starting_address}: {values}\n")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    ip_address = '192.168.0.101'
    port = 502
    file_path = "C:/Users/admin/Desktop/func16_results.txt"

    client = ModbusClient(ip_address, port=port)
    if client.connect():
        print("Connected to the Modbus server.")
        for address in range(0, 65536, 10):  # Similar to the coils, adjust range and step as needed
            register_values = [random.randint(0, 65535) for _ in range(10)]  # Example: Writing 10 registers at a time
            write_multiple_registers_example(client, address, register_values, file_path)
            time.sleep(0.01)
    else:
        print("Failed to connect to the Modbus server.")
    client.close()

if __name__ == '__main__':
    main()
