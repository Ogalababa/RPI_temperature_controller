# ！/usr/bin/python3
# coding:utf-8
# /run.mi_temp.py
from bluepy.btle import Scanner, DefaultDelegate
import time
import logging

# 设置logging基础配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])  # 输出到控制台
logger = logging.getLogger(__name__)


class ScanDelegate(DefaultDelegate):
    def __init__(self, target_mac):
        DefaultDelegate.__init__(self)
        self.target_mac = target_mac.lower()
        self.found = False
        self.temperature = None
        self.humidity = None

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr.lower() == self.target_mac:
            for (adtype, desc, value) in dev.getScanData():
                if desc == "16b Service Data" and value.startswith("95fe") and len(value) == 40:
                    self.temperature, self.humidity = parse_mi_service_data(value)
                    logger.info(f"Temperature: {self.temperature}°C, Humidity: {self.humidity}%")
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


def scan_mi_temp(target_mac="58:2D:34:30:53:58", scan_time=2, max_retries=5, retry_delay=1):
    scanner = Scanner().withDelegate(ScanDelegate(target_mac))
    counter = 0
    while not scanner.delegate.found and counter < max_retries:
        start_time = time.time()
        scanner.scan(scan_time)
        end_time = time.time()
        counter += 1
        if not scanner.delegate.found:
            logger.info(f"Attempt {counter}/{max_retries}: Target data not found, rescanning...")
            time.sleep(retry_delay)
        logger.info(f"Scan duration: {end_time - start_time:.2f} seconds")

    if scanner.delegate.found:
        return scanner.delegate.temperature, scanner.delegate.humidity
    else:
        logger.info("Failed to find target device after maximum retries.")
        return False


# 调用函数并获取温度和湿度
if __name__ == "__main__":
    temperature, humidity = scan_mi_temp(target_mac="58:2D:34:30:53:58", scan_time=2)
    if temperature and humidity:
        logger.info(f"Final Temperature: {temperature}°C, Final Humidity: {humidity}%")
    else:
        logger.info("Failed to retrieve temperature and humidity data.")
