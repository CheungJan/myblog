"""
Gunicorn 配置文件
"""
import multiprocessing

# 绑定的 IP 和端口
bind = "0.0.0.0:$PORT"

# 工作进程数量
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "gevent"

# 超时时间
timeout = 120

# 日志级别
loglevel = "info"
