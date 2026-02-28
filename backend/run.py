# 非 Windows 下使用 eventlet 需在其它导入前 monkey_patch，避免 Flask-SocketIO WebSocket 报错；Windows 下 eventlet 不兼容，使用 threading
import sys
if sys.platform != "win32":
    try:
        import eventlet
        eventlet.monkey_patch()
    except ImportError:
        pass

import os
from pathlib import Path
from dotenv import load_dotenv
from app import create_app

# 固定从 backend 目录加载 .env，避免从项目根启动时读不到配置
_env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=_env_path)

app = create_app()

if __name__ == '__main__':
    config_name = os.getenv('FLASK_ENV', 'development')
    port = int(os.getenv('PORT', 5000))
    # 使用 SocketIO 启动，与 Flask 同进程，支持 WebSocket 推送
    app.socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=(config_name == 'development')
    )