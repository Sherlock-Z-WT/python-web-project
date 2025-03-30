import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from ping3 import ping


class Scanner:
    def __init__(self):
        self.progress = 0
        self.reachable_ips = []
        self.is_scanning = False
        self.start_time = None
        self.lock = threading.Lock()

    def ping(self, ip):
        try:
            response = ping(ip, timeout=1)
            return response is not None
        except:
            return False

    def scan_ip(self, subnet, start, end):
        self.start_time = time.time()
        self.progress = 0
        self.reachable_ips = []
        self.checked_ips = 0  # 新增：全局计数器

        ips = [f"{subnet}.{i}" for i in range(start, end + 1)]
        total = len(ips)

        def check_ip(ip):
            if self.ping(ip):
                with self.lock:
                    self.reachable_ips.append(ip)

            with self.lock:
                self.checked_ips += 1  # 每检查一个IP就+1
                self.progress = min(self.checked_ips / total * 100, 100)  # 确保不超过100%

        with ThreadPoolExecutor(max_workers=min(os.cpu_count() * 4, 100)) as executor:
            executor.map(check_ip, ips)

        return self.reachable_ips, total

    def start_scan(self, subnet, start, end):
        self.is_scanning = True
        self.progress = 0
        self.reachable_ips = []
        self.start_time = time.time()

        def scan_task():
            self.scan_ip(subnet, start, end)
            self.is_scanning = False

        thread = threading.Thread(target=scan_task)
        thread.start()
