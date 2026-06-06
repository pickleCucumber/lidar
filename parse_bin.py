#!/usr/bin/env python3
import serial
import struct
import csv
import time
import math
from datetime import datetime

SERIAL_PORT = '/dev/serial0'   
BAUDRATE = 230400
HEADER = 0x54
PACKET_SIZE = 48
POINTS_PER_PACKET = 12

def parse_packet(packet):
    """
    Распаковывает пакет LD06.
    Возвращает список словарей: [{'angle': float_deg, 'dist': int_mm, 'intens': int}, ...]
    """
    if packet[0] != HEADER:
        return []
    # Структура (little-endian):
    # [0] header (0x54)
    # [1] ver_len (младшие 5 бит = длина данных = 12*3 = 36)
    # [2:4] speed (0.01 град/с)
    # [4:6] start_angle (0.01 град)
    # [6:42] 12 точек по 3 байта: расстояние (2 байта, мм), интенсивность (1 байт)
    # [42:44] end_angle (0.01 град)
    # [44:46] timestamp (мс)
    # [46] crc8
    start_angle = struct.unpack('<H', packet[4:6])[0] / 100.0   # градусы
    end_angle   = struct.unpack('<H', packet[42:44])[0] / 100.0
    # Обработка перехода через 0° (end_angle может быть меньше start_angle)
    if end_angle < start_angle:
        end_angle += 360.0
    angle_step = (end_angle - start_angle) / (POINTS_PER_PACKET - 1) if POINTS_PER_PACKET > 1 else 0

    points = []
    for i in range(POINTS_PER_PACKET):
        offset = 6 + i * 3
        dist = struct.unpack('<H', packet[offset:offset+2])[0]
        intens = packet[offset+2]
        angle = start_angle + i * angle_step
        # Нормализуем угол в [0, 360)
        angle = angle % 360.0
        points.append({
            'angle': angle,
            'dist': dist,
            'intens': intens
        })
    return points

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"Подключён к {SERIAL_PORT} на скорости {BAUDRATE}")
    except serial.SerialException as e:
        print(f"Ошибка открытия порта: {e}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"lidar_polar_{timestamp}.csv"
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Angle_deg", "Distance_mm", "Intensity"])
        total_points = 0
        print(f"Сохранение в {csv_filename} (нажмите Ctrl+C для остановки)")
        try:
            while True:
                byte = ser.read(1)
                if not byte:
                    continue
                if byte[0] == HEADER:
                    packet = byte + ser.read(PACKET_SIZE - 1)
                    if len(packet) == PACKET_SIZE:
                        points = parse_packet(packet)
                        for p in points:
                            # Фильтр недостоверных расстояний (опционально)
                            if 0 < p['dist'] < 12000:
                                writer.writerow([f"{p['angle']:.2f}", p['dist'], p['intens']])
                                total_points += 1
                        if total_points % 200 == 0:
                            print(f"Записано точек: {total_points}")
        except KeyboardInterrupt:
            print(f"\nОстановлено. Всего точек: {total_points}")
        finally:
            ser.close()
    print(f"Данные сохранены в {csv_filename}")

if __name__ == "__main__":
    main()
