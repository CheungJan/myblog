"""
Flask 应用程序入口点
"""
import os
from myblog import create_app

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG', 'production'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
