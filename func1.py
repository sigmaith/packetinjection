from pymodbus.client import ModbusTcpClient as ModbusClient
import time

def read_coils(client, file_path):
    with open(file_path, "w") as file:
        for address in range(65536):
            try:
                response = client.read_coils(address, 1)
                if response.isError():
                    file.write(f"Error reading coil at address {address}: {response}\n")
                else:
                    file.write(f"Successfully read coil at address {address}: {response.bits[0]}\n")
            except Exception as e:
                file.write(f"Modbus communication error at address {address}: {e}\n")
            time.sleep(0.01)

def main():
    ip_address = '192.168.0.101'
    port = 502
    file_path = "C:/Users/admin/Desktop/func01_results.txt"
    client = ModbusClient(ip_address, port=port)
    if client.connect():
        print("Connected to the Modbus server.")
        read_coils(client, file_path)
    else:
        print("Failed to connect to the Modbus server.")
    client.close()

if __name__ == '__main__':
    main()