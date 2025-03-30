# 网络设备扫描器 Web 版「本项目可扩展为企业内网设备健康监测系统，适用于IT运维场景」  

##  项目概述
基于 Flask 开发的轻量级网络设备扫描工具，可快速检测局域网内存活设备。支持：
- 多线程并发扫描
- 实时进度展示
- 响应式 Web 界面

##  技术栈
- **后端**：Python + Flask
- **前端**：HTML5 + CSS3
- **核心功能**：`ping3` + `concurrent.futures`

##  项目亮点
1. 命令行工具 Web 化改造
2. 智能线程池管理（自动计算最优线程数）
3. 跨平台兼容性设计

##  快速开始
```bash
# 克隆项目
git clone https://github.com/yourname/network-scanner.git

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py

 适用场景
企业内网设备盘点
网络故障快速定位
运维自动化工具集成

