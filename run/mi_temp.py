# ！/usr/bin/python3
# coding:utf-8
# sys
# /run.mi_temp.py
from bluepy.btle import Scanner, DefaultDelegate


class ScanDelegate(DefaultDelegate):
    def __init__(self, target_mac):
        DefaultDelegate.__init__(self)
        self.target_mac = target_mac.lower()
        self.found = False
        self.temperature = None
        self.humidity = None

    def handle_discovery(self, dev, is_new_dev, is_new_data):
        if dev.addr.lower() == self.target_mac:
            for (adtype, desc, value) in dev.getScanData():
                if desc == "16b Service Data" and value.startswith("95fe") and len(value) == 40:
                    self.temperature, self.humidity = parse_mi_service_data(value)
                    print(f"Temperature: {self.temperature}°C, Humidity: {self.humidity}%")
                    self.found = True
                    break


def parse_mi_service_data(service_data):
    # 将16进制字符串转换为字节数组
    data_bytes = bytes.fromhex(service_data)

    # 假设温度数据位于字节位置倒数第4和第3（字节数组索引从0开始）
    temperature_raw = int.from_bytes(data_bytes[-4:-2], byteorder='little', signed=True)
    temperature = temperature_raw / 10.0

    # 假设湿度数据位于字节位置倒数第2和第1
    humidity_raw = int.from_bytes(data_bytes[-2:], byteorder='little', signed=False)
    humidity = humidity_raw / 10.0

    return temperature, humidity


def scan_mi_temp(target_mac="58:2D:34:30:53:58", scan_time=2, max_retries=5):
    scanner = Scanner().withDelegate(ScanDelegate(target_mac))
    counter = 0
    while not scanner.delegate.found and counter < max_retries:
        scanner.scan(scan_time)
        counter += 1
        if not scanner.delegate.found:
            print(f"Attempt {counter}/{max_retries}: Target data not found, rescanning...")

    if scanner.delegate.found:
        return scanner.delegate.temperature, scanner.delegate.humidity
    else:
        print("Failed to find target device after maximum retries.")
        return False


# 调用函数并获取温度和湿度
if __name__ == "__main__":
    temperature, humidity = scan_mi_temp(target_mac="58:2D:34:30:53:58", scan_time=2)
    print(f"Final Temperature: {temperature}°C, Final Humidity: {humidity}%")