#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置文件：从环境变量读取；若存在 backend/.env 则加载（与后端配置方式一致）。
在项目根目录执行 database 脚本即可。
"""
import os
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent / 'backend'
_env_path = _backend_dir / '.env'
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_env_path)

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
