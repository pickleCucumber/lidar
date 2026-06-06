import serial
import time
import struct
from datetime import datetime

SERIAL_PORT = '/dev/serial0' 
BAUDRATE = 230400            
HEADER_BYTE = 0xFA           
PACKET_SIZE = 42             

def main():
    try:
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
            print(f"Парсинг данных с {SERIAL_PORT}")
            log_filename = f"lidar_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
            print(f"данные будут сохранены в файл: {log_filename}")
            with open(log_filename, "wb") as f:
                while True:
                    if ser.read() == bytes([HEADER_BYTE]):
                        packet_remainder = ser.read(PACKET_SIZE - 1)
                        if len(packet_remainder) == PACKET_SIZE - 1:
                            full_packet = bytes([HEADER_BYTE]) + packet_remainder
                            
                            f.write(full_packet)
                            
                        else:
                            print("Не удалось прочитать полный пакет.")

    except serial.SerialException as e:
        print(f"Ошибка с портом: {e}")
    except KeyboardInterrupt:
        print("\nЗапись остановлена.")

if __name__ == "__main__":
    main()
