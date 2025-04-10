from flask import Flask, render_template, request, jsonify, redirect, url_for
from scanner import Scanner#自定义扫描器模块
import logging
from logging.handlers import RotatingFileHandler
#------------------flask应用初始化
# 创建 Flask 应用实例
app = Flask(__name__)

# 配置日志
def configure_logging():
    #配置日志记录系统
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    #文件日志（滚动记录，最大1mb，保留五个）
    file_handler = RotatingFileHandler('app.log', maxBytes=1e6, backupCount=5)
    file_handler.setFormatter(formatter)
    #控制台日志
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    #应用日志配置
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.DEBUG)

configure_logging()

# 初始化扫描器
scanner = Scanner()
#路由定义
@app.route('/start-scan', methods=['POST'])
def start_scan():
    """处理扫描启动请求"""
    #获取表单参数
    subnet = request.form.get('subnet', '172.22.53')
    start = int(request.form.get('start', 1))
    end = int(request.form.get('end', 255))
    #非阻塞启动扫描
    if not scanner.is_scanning:
        scanner.start_scan(subnet, start, end)
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already_running"})

@app.route('/scan-progress')
def scan_progress():
    """提供扫描进度查询接口"""
    return jsonify({
        'progress': scanner.progress,#当前进度百分比
        'online': len(scanner.reachable_ips),#在线设备数
        'reachable_ips': scanner.reachable_ips,#在线ip列表
        'is_scanning': scanner.is_scanning#是否正在扫描
    })

@app.route('/', methods=['GET', 'POST'])
def index():
    """主页面路由"""
    if request.method == 'POST':
        #处理表单提交
        subnet = request.form.get('subnet', '172.22.53')
        start = int(request.form.get('start', 1))
        end = int(request.form.get('end', 255))
        #输入验证
        if not subnet.replace('.', '').isdigit():
            return render_template('index.html', error="子网格式应为 xxx.xxx.xxx")
        if not (1 <= start <= end <= 255):
            return render_template('index.html', error="IP范围应为 1-255")
        #启动扫描并跳转到结果页面
        scanner.start_scan(subnet, start, end)
        return redirect(url_for('results', subnet=subnet, start=start, end=end))
    #处理GET请求
    return render_template('index.html')

@app.route('/results')
def results():
    """扫描结果展示页面"""
    #从URL参数获取扫描范围
    subnet = request.args.get('subnet', '172.22.53')
    start = int(request.args.get('start', 1))
    end = int(request.args.get('end', 255))
    #渲染结果模板
    return render_template('results.html',  # 修复参数传递
        subnet=subnet,
        start=start,
        end=end
    )
#主程序入口
if __name__ == '__main__':
    """启动开发服务器"""
    app.run(debug=True, port=5000)#开启调试模式，端口为5000 
