import os
from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 获取配置
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=(config_name == 'development')
    )