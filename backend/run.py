import os
from pathlib import Path
from dotenv import load_dotenv
from app import create_app

# 固定从 backend 目录加载 .env，避免从项目根启动时读不到配置
_env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=_env_path)

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