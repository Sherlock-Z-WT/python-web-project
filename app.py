from flask import Flask, render_template, request, jsonify, redirect, url_for
from scanner import Scanner  # 导入之前定义的扫描器类
import time

# 创建Flask应用实例
app = Flask(__name__)
# 初始化扫描器实例
scanner = Scanner()

@app.route('/start-scan', methods=['POST'])
def start_scan():
    """处理扫描开始的AJAX请求"""
    # 获取表单参数，设置默认值
    subnet = request.form.get('subnet', '172.22.53')  # 默认扫描172.22.53.x网段
    start = int(request.form.get('start', 1))        # 默认起始IP尾数
    end = int(request.form.get('end', 255))          # 默认结束IP尾数

    # 启动扫描（非阻塞方式）
    scanner.start_scan(subnet, start, end)

    # 等待扫描完成
    while scanner.is_scanning:  # 循环检查扫描状态
        time.sleep(0.1)         # 避免CPU占用过高

    # 返回JSON格式结果
    return jsonify({
        "status": "completed",
        "reachable_ips": scanner.reachable_ips,  # 可达IP列表
        "total": end - start + 1,                # 总扫描IP数
        "progress": 100                          # 进度百分比
    })

@app.route('/scan-progress')
def scan_progress():
    """提供扫描进度查询接口"""
    return jsonify({
        'progress': scanner.progress,           # 当前进度
        'online': len(scanner.reachable_ips),   # 在线设备数
        'reachable_ips': scanner.reachable_ips, # 在线IP列表
        'is_scanning': scanner.is_scanning      # 是否正在扫描
    })

@app.route('/', methods=['GET', 'POST'])
def index():
    """主页面路由"""
    if request.method == 'POST':
        # 获取表单数据
        subnet = request.form.get('subnet', '172.22.53')
        start = int(request.form.get('start', 1))
        end = int(request.form.get('end', 255))

        # 输入验证
        if not subnet.replace('.', '').isdigit():
            return render_template('index.html',
                                 error="子网格式应为 xxx.xxx.xxx")
        if not (1 <= start <= end <= 255):
            return render_template('index.html',
                                 error="IP范围应为 1-255")

        # 启动扫描并跳转到结果页
        scanner.start_scan(subnet, start, end)
        return redirect(url_for('results',
                              subnet=subnet,
                              start=start,
                              end=end))

    # GET请求返回页面
    return render_template('index.html')

@app.route('/results')
def results():
    """扫描结果展示页"""
    # 从URL参数获取扫描范围
    subnet = request.args.get('subnet', '172.22.53')
    start = int(request.args.get('start', 1))
    end = int(request.args.get('end', 255))

    # 渲染结果模板
    return render_template('results.html',
                         subnet=subnet,
                         start=start,
                         end=end)

if __name__ == '__main__':
    # 启动开发服务器
    app.run(debug=True, port=5000)  # debug模式，端口5000
