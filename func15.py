import sys
from pymodbus.client import ModbusTcpClient as ModbusClient
import time
import random

def write_multiple_coils_example(client, starting_address, values, file_path):
    try:
        response = client.write_coils(starting_address, values)
        with open(file_path, "a+") as file:
            if response.isError():
                error_code = response.exception_code
                file.write(f"Error writing coils starting at {starting_address}: {error_code}\n")
            else:
                file.write(f"Successfully wrote coils starting at {starting_address}: {values}\n")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    ip_address = '192.168.0.101'
    port = 502
    file_path = "C:/Users/admin/Desktop/func15_results.txt"

    client = ModbusClient(ip_address, port=port)
    if client.connect():
        print("Connected to the Modbus server.")
        for address in range(0, 65536, 10):  # Adjust range and step depending on how many coils you want to write each time
            coil_values = [random.choice([True, False]) for _ in range(10)]  # Example: Writing 10 coils at a time
            write_multiple_coils_example(client, address, coil_values, file_path)
            time.sleep(0.01)
    else:
        print("Failed to connect to the Modbus server.")
    client.close()

if __name__ == '__main__':
    main()
