# -*- coding: utf-8 -*-
"""请求相关工具：客户端真实 IP、是否本机访问（供设备/Agent 路由共用）"""
from flask import request


def get_client_real_ip():
    """
    获取当前请求的客户端真实 IP。
    优先使用 X-Forwarded-For 首段（原始客户端），其次 X-Real-IP，最后 request.remote_addr。
    反向代理/前端代理需正确设置 X-Forwarded-For，否则内网访问会被误判为本机。
    """
    forwarded = (request.headers.get('X-Forwarded-For') or '').strip()
    real_ip = (forwarded.split(',')[0].strip() if forwarded else None) or request.headers.get('X-Real-IP') or request.remote_addr or ''
    return (real_ip or '').strip()


def is_platform_host():
    """
    当前请求是否来自部署平台的本机（用于区分本机用户与远程访问用户）。
    仅将 127.0.0.1 / ::1 视为本机；内网 IP（192.168.x.x、10.x.x.x 等）一律视为远程。
    确保电脑 B 内网访问电脑 A 时不会被当作本机，避免远程用户看到/操作本机 adb。
    """
    real_ip = get_client_real_ip()
    if not real_ip:
        return False
    # 环回地址视为本机（含 IPv6 映射的 127.0.0.1）
    loopback = real_ip in ('127.0.0.1', '::1', 'localhost') or real_ip.lower() == '::ffff:127.0.0.1'
    if loopback:
        return True
    # IPv6 映射的 IPv4：取后半段再判断
    if real_ip.lower().startswith('::ffff:'):
        real_ip = real_ip[7:].strip()
    if real_ip.startswith('192.168.') or real_ip.startswith('10.') or real_ip.startswith('172.'):
        return False
    if real_ip.startswith('fe80:') or ('%' in real_ip):
        return False
    return False
