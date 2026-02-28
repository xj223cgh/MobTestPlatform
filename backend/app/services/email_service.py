# -*- coding: utf-8 -*-
"""QQ 邮箱发信服务：登录验证码、找回密码链接。返回 (成功, 错误标识) 便于区分收件人无效与其它错误。"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

from flask import current_app

logger = logging.getLogger(__name__)


def send_email(to_email, subject, body_text, body_html=None):
    """
    使用 QQ 邮箱 SMTP 发送邮件。
    返回 (True, None) 成功；(False, 'recipient_refused') 收件人无效/无法接收；(False, None) 其它发送失败。
    """
    host = current_app.config.get('SMTP_HOST', 'smtp.qq.com')
    port = current_app.config.get('SMTP_PORT', 465)
    use_ssl = current_app.config.get('SMTP_USE_SSL', True)
    user = current_app.config.get('SMTP_USER')
    password = current_app.config.get('SMTP_PASSWORD')
    from_name = current_app.config.get('SMTP_FROM_NAME', '移动测试平台')

    if not user or not password:
        logger.warning('SMTP_USER or SMTP_PASSWORD not set, skip sending email')
        return False, None

    from_addr = user
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    h = Header(from_name, 'utf-8')
    from_name_str = h.encode() if hasattr(h, 'encode') and callable(getattr(h, 'encode', None)) else str(h)
    if isinstance(from_name_str, bytes):
        from_name_str = from_name_str.decode('ascii')
    msg['From'] = formataddr((from_name_str, from_addr))
    msg['To'] = to_email

    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    if body_html:
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=15) as server:
                server.login(user, password)
                server.sendmail(from_addr, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.starttls()
                server.login(user, password)
                server.sendmail(from_addr, [to_email], msg.as_string())
        logger.info('Email sent to %s', to_email)
        return True, None
    except smtplib.SMTPRecipientsRefused:
        logger.warning('SMTP recipients refused for %s', to_email)
        return False, 'recipient_refused'
    except smtplib.SMTPResponseException as e:
        # 550 等：邮箱不存在或拒收
        if e.smtp_code == 550 or (e.smtp_code >= 500 and 'mailbox' in (e.smtp_error or '').lower()):
            logger.warning('SMTP recipient error for %s: %s %s', to_email, e.smtp_code, e.smtp_error)
            return False, 'recipient_refused'
        logger.exception('SMTP error for %s: %s', to_email, e)
        return False, None
    except Exception as e:
        err_str = str(e).lower()
        if '550' in err_str or 'mailbox' in err_str or 'recipient' in err_str or 'not found' in err_str:
            logger.warning('Email send failed (recipient): %s', e)
            return False, 'recipient_refused'
        logger.exception('Send email failed: %s', e)
        return False, None


def send_login_code(to_email, code):
    """发送登录验证码（6 位数字）。返回 (ok, error_key)。"""
    subject = '【移动测试平台】登录验证码'
    body = f'''您好，

您正在使用邮箱验证码登录移动测试平台，验证码为：

  {code}

验证码 5 分钟内有效，请勿泄露给他人。如非本人操作，请忽略本邮件。
'''
    return send_email(to_email, subject, body)


def send_bind_verify_code(to_email, code):
    """发送邮箱绑定验证码（配置邮箱时验证真实性）。返回 (ok, error_key)。"""
    subject = '【移动测试平台】邮箱绑定验证码'
    body = f'''您好，

您正在绑定/修改移动测试平台账号邮箱，验证码为：

  {code}

验证码 5 分钟内有效，请勿泄露给他人。如非本人操作，请忽略本邮件。
'''
    return send_email(to_email, subject, body)


def send_unbind_verify_code(to_email, code):
    """发送解除邮箱绑定验证码。返回 (ok, error_key)。"""
    subject = '【移动测试平台】解除邮箱绑定验证码'
    body = f'''您好，

您正在解除移动测试平台账号的邮箱绑定，验证码为：

  {code}

验证码 5 分钟内有效，请勿泄露给他人。如非本人操作，请忽略本邮件。
'''
    return send_email(to_email, subject, body)


def send_reset_password_link(to_email, reset_link):
    """发送找回密码链接。返回 (ok, error_key)。"""
    subject = '【移动测试平台】重置密码'
    body = f'''您好，

您已申请重置移动测试平台账号密码，请点击以下链接设置新密码（30 分钟内有效）：

{reset_link}

如非本人操作，请忽略本邮件并妥善保管账号。
'''
    html = f'''<p>您好，</p>
<p>您已申请重置移动测试平台账号密码，请点击以下链接设置新密码（30 分钟内有效）：</p>
<p><a href="{reset_link}">{reset_link}</a></p>
<p>如非本人操作，请忽略本邮件。</p>
'''
    return send_email(to_email, subject, body, html)
