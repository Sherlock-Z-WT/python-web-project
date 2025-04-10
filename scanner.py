
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from ping3 import ping
import subprocess  # 添加subprocess作为备用方案
class Scanner:
    def __init__(self):
        # 初始化扫描状态变量
        self.progress = 0  # 扫描进度百分比
        self.reachable_ips = []  # 存储可达IP地址列表
        self.is_scanning = False  # 扫描状态标志
        self.lock = threading.Lock()  # 线程锁，防止多线程数据竞争
        self.total_ips = 0  # 需要扫描的IP总数
        self.checked_ips = 0  # 已扫描的IP计数

    def ping(self, ip):
        """执行Ping检测的混合方法"""
        try:
            # 方法1：优先使用ping3库（跨平台）
            response = ping(ip, timeout=2)  # 设置2秒超时
            if response is not None:  # 如果收到响应
                return True

            # 方法2：如果ping3失败，使用系统ping命令（备用方案）
            param = '-n' if os.name == 'nt' else '-c'#windows用-n，其他系统用-c
            command = ['ping', param, '1', '-W', '2', ip]  # 构造ping命令：
            # -n/-c 1: 只发送1个包
            # -W 2: 等待2秒超时
            # ip: 目标地址
            output = subprocess.run(
                command,
                stdout=subprocess.PIPE,  # 捕获标准输出
                stderr=subprocess.PIPE,  # 捕获错误输出
                timeout=2  # 设置2秒超时
            )
            return output.returncode == 0  # 返回码为0表示成功
        except Exception as e:
            print(f"⚠️ Ping {ip} 出错: {e}")
            return False

    def scan_ip(self, subnet, start, end):
        """核心扫描方法"""
        # 初始化扫描指标
        self.start_time = time.time()  # 记录开始时间
        self.progress = 0
        self.reachable_ips = []
        self.checked_ips = 0

        # 生成要扫描的IP列表
        ips = [f"{subnet}.{i}" for i in range(start, end + 1)]
        self.total_ips = len(ips)  # 设置总数

        def check_ip(ip):
            """线程任务：检查单个IP"""
            try:
                is_online = self.ping(ip)  # 执行ping检测
                with self.lock:  # 获取线程锁让同一时间只有一个线程能修改这些共享数据，其他线程必须等待。
                    if is_online:
                        self.reachable_ips.append(ip)  # 记录可达IP
                    # 计算进度（已完成数/总数 * 100）上限100
                    self.progress = min(self.checked_ips / self.total_ips * 100, 100)
            except Exception as e:
                print(f"扫描 {ip} 时出错: {e}")
            finally:
                with self.lock:  # 确保即使出错也更新进度
                    self.checked_ips += 1
                    self.progress = min(self.checked_ips / self.total_ips * 100, 100)

        # 使用线程池并发执行（智能控制线程数）
        max_workers = min(30, (os.cpu_count() or 1) * 2)
        # 获取电脑的cpu核心数，计算线程数。 默认取CPU核心数*2.如果os.cpu_count()返回4就用4，如果无法获取核心数,返回None或者0就默认用1
        #每个cpu核心可以同时处理两个线程
        #30是设置最大不超过30个线程
        with ThreadPoolExecutor(max_workers=max_workers) as executor:#创建线程池，设置最大并发线程数，执行完毕后自动关闭线程池
            list(executor.map(check_ip, ips))#map作用就是将check_ip函数运用到所有ip上

        # 扫描完成处理
        self.progress = 100  # 强制设置为100%（防止浮点误差）
        self.is_scanning = False
        return self.reachable_ips, self.total_ips

    def start_scan(self, subnet, start, end):
        """启动扫描的入口方法"""
        if self.is_scanning:
            print("⚠️ 扫描正在进行中，请等待完成")
            return

        self.is_scanning = True
        # 创建并启动扫描线程（守护线程模式）
        thread = threading.Thread(
            target=self.scan_ip,  # 指定要运行的方法
            args=(subnet, start, end),  # 传入参数
            daemon=True  # 标记为守护线程（主程序退出时自动终止线程）
        )

        thread.start()  # 启动线程
