#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置文件。与 backend 一致：从环境变量读取（优先 backend/.env），便于 main/kingsoft 等不同分支用不同库名而代码一致。
"""
import os
from pathlib import Path

# 与 backend 一致：从 backend/.env 加载环境变量（跑 database 脚本时在项目根执行即可）
_backend_dir = Path(__file__).resolve().parent.parent / 'backend'
_env_path = _backend_dir / '.env'
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_env_path)
    except Exception:
        pass

_db = os.environ.get('MYSQL_DATABASE') or 'mobile_test_platform'

# 数据库连接配置（与 backend/app/config/config.py 对齐）
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST') or 'localhost',
    'user': os.environ.get('MYSQL_USER') or 'root',
    'password': os.environ.get('MYSQL_PASSWORD') or '123456',
    'database': _db,
    'charset': 'utf8mb4'
}

# 数据库名称（建库/删库脚本用）
DB_NAME = _db
