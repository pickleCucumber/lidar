import struct
import csv


PACKET_SIZE = 42   
HEADER_BYTE = 0xFA 
FIELDS = [
    ("header", "B"),        # 1 байт, должен быть 0xFA
    ("index", "B"),         # 1 байт, индекс пакета 
    ("speed", "H"),         # 2 байта, скорость вращения (0.1 градуса/сек?)
    ("start_angle", "H"),   # 2 байта, начальный угол (0.01 градуса?)
    ("distances", "12H"),   # 12*2=24 байта, 12 расстояний (по 2 байта каждое)
    ("intensities", "12B"), # 12*1=12 байт, интенсивность для каждого луча
]

def parse_packet(data):
    """пакет согласно структуре FIELDS."""
    offset = 0
    result = {}
    for name, fmt in FIELDS:
        size = struct.calcsize(fmt)
        values = struct.unpack_from(f"<{fmt}", data, offset)  # little-endian
        offset += size
        if len(values) == 1:
            result[name] = values[0]
        else:
            result[name] = values
    return result

def main():
    filename = input("Введите имя .bin файла: ").strip()
    if not filename:
        filename = "lidar_data_20260607_005132.bin" 
    
    with open(filename, "rb") as f:
        raw = f.read()
    
    print(f"Размер файла: {len(raw)} байт")
    print(f"Ожидаемое количество пакетов (по {PACKET_SIZE} байт): {len(raw) // PACKET_SIZE}")
    
    packets = []
    i = 0
    while i <= len(raw) - PACKET_SIZE:
        if raw[i] == HEADER_BYTE:
            packet_data = raw[i:i+PACKET_SIZE]
            packets.append(packet_data)
            i += PACKET_SIZE
        else:
            i += 1
    
    print(f"Найдено валидных пакетов: {len(packets)}")
    
    if not packets:
        print("Не найдено ни одного пакета с заголовком 0xFA.")
        print("Показываю первые 64 байта файла в HEX для анализа:")
        print(raw[:64].hex(' ', 16))
        return
    
    print("\n--- Расшифровка первых 5 пакетов ---")
    for idx, pkt in enumerate(packets[:5]):
        try:
            parsed = parse_packet(pkt)
            print(f"Пакет {idx}: {parsed}")
        except Exception as e:
            print(f"Пакет {idx}: ошибка распаковки - {e}")
            print(f"  HEX: {pkt.hex(' ', 16)}")
    
    out_csv = filename.replace('.bin', '_parsed.csv')
    with open(out_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        headers = []
        for name, fmt in FIELDS:
            size = struct.calcsize(fmt)
            if size > 1 and 'H' in fmt:
                count = size // 2
                headers.extend([f"{name}_{j}" for j in range(count)])
            else:
                headers.append(name)
        writer.writerow(headers)
        
        for pkt in packets:
            try:
                parsed = parse_packet(pkt)
                row = []
                for name, fmt in FIELDS:
                    val = parsed[name]
                    if isinstance(val, tuple):
                        row.extend(val)
                    else:
                        row.append(val)
                writer.writerow(row)
            except:
                continue
    print(f"\nданные сохранены в {out_csv}")

if __name__ == "__main__":
    main()
