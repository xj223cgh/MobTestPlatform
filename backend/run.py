"""应用入口：加载 .env、创建应用，开发环境下由 SocketIO 提供 WebSocket。"""
import sys
# 非 Windows 下优先 monkey_patch，供 SocketIO 的 eventlet 模式使用
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

_env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=_env_path)

app = create_app()

if __name__ == '__main__':
    config_name = os.getenv('FLASK_ENV', 'development')
    port = int(os.getenv('PORT', 5000))
    app.socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=(config_name == 'development')
    )