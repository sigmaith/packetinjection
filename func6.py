import sys
from pymodbus.client import ModbusTcpClient as ModbusClient
import time
import random

def write_single_register_example(client, reference_number, value, file_path):
    try:
        response = client.write_register(reference_number, value)
        # Opening the file in append mode, create if not exists ('a+')
        with open(file_path, "a+") as file:
            if response.isError():
                file.write(f"Error writing register at reference {reference_number}: {response}\n")
            else:
                file.write(f"Successfully wrote register at reference {reference_number}: {value}\n")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    ip_address = '192.168.0.101'
    port = 502
    # Specify the correct path on your desktop for file saving
    file_path = "C:/Users/admin/Desktop/func06_results.txt"

    client = ModbusClient(ip_address, port=port)
    if client.connect():
        print("Connected to the Modbus server.")
        # Iterating through all possible register addresses
        for reference_number in range(65536):
            write_value = random.randint(0, 65535)  # Random value to write
            write_single_register_example(client, reference_number, write_value, file_path)
            time.sleep(0.01)  # Reduce speed to prevent overloading the network
    else:
        print("Failed to connect to the Modbus server.")
    client.close()

if __name__ == '__main__':
    main()
