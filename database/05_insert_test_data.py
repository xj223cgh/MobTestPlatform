#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 插入测试数据

插入内容：用户（与原有一致）+ WPS 邮箱业务 + WPS 会议业务模拟数据（项目、迭代、需求、用例库、任务、评审、设备、报告等）。
"""

import pymysql
import json
import uuid
import hashlib
import shutil
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from database.config import DB_CONFIG

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset']
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


def insert_wps_email_business_data(connection):
    """
    插入 WPS 邮箱业务模拟数据（不包含用户；依赖现有 users 数据）。
    包含：单项目、迭代、需求、用例库、用例、评审、任务文件夹、任务、快照、执行记录、设备、设备脚本任务、报告。
    """
    cursor = connection.cursor()
    now = datetime.now()
    time_fmt = '%Y-%m-%d %H:%M:%S'

    cursor.execute("SELECT id FROM users ORDER BY id")
    user_ids = [row[0] for row in cursor.fetchall()]
    if not user_ids:
        print("错误：未找到任何用户，请先插入用户数据。")
        return False
    uid_owner = user_ids[0]
    uid_creator = user_ids[0]
    uid_tester1 = user_ids[1] if len(user_ids) > 1 else user_ids[0]
    uid_tester2 = user_ids[2] if len(user_ids) > 2 else user_ids[0]
    uid_reviewer = user_ids[2] if len(user_ids) > 2 else user_ids[1]

    print("插入项目（WPS 邮箱业务）...")
    proj_start = (now - timedelta(days=120)).strftime(time_fmt)
    proj_end = (now + timedelta(days=90)).strftime(time_fmt)
    cursor.execute("""
        INSERT INTO projects (project_name, description, status, owner_id, creator_id, start_date, end_date, tags, priority, doc_url, pipeline_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        'WPS邮箱',
        'WPS 邮箱客户端相关功能与专项测试，包含写邮件、收件箱、设置、账号同步等模块。',
        'in_progress', uid_owner, uid_creator, proj_start, proj_end,
        json.dumps(['WPS', '邮箱', '移动端']), 'high',
        'https://docs.example.com/wps-email', 'https://pipeline.example.com/wps-email',
    ))
    project_id = cursor.lastrowid
    for i, uid in enumerate(user_ids[:6]):
        role = 'owner' if uid == uid_owner else ('manager' if i == 1 else 'tester')
        cursor.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s, %s, %s)", (project_id, uid, role))

    print("插入迭代...")
    iter_rows = [
        ('V1.0.0', '首版发信与收件箱', 'completed', -120, -80),
        ('V1.1.0', '发件箱与草稿箱', 'completed', -75, -45),
        ('V1.2.0', '设置与账号同步', 'completed', -40, -15),
        ('V2.0.0', '标签、搜索与过滤', 'active', -10, 25),
        ('V2.1.0', '多账号与通知', 'active', 5, 45),
        ('V2.2.0', '专项与体验优化', 'planning', 40, 75),
    ]
    iteration_ids = []
    for name, goal, status, start_delta, end_delta in iter_rows:
        start_d = (now + timedelta(days=start_delta)).strftime(time_fmt)
        end_d = (now + timedelta(days=end_delta)).strftime(time_fmt)
        cursor.execute("""
            INSERT INTO iterations (project_id, iteration_name, description, goal, status, start_date, end_date, version, created_by, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (project_id, name, f'WPS邮箱 {name} 迭代', goal, status, start_d, end_d, name, uid_creator, uid_creator))
        iteration_ids.append(cursor.lastrowid)

    print("插入需求...")
    req_rows = [
        ('写邮件与发信', '新建/编辑邮件、收件人/抄送/密送、主题与正文', iteration_ids[0], 'completed'),
        ('附件与签名', '添加附件、邮件签名、格式设置', iteration_ids[0], 'completed'),
        ('收件箱与阅读', '收件箱列表、邮件阅读、未读标记、预览', iteration_ids[0], 'completed'),
        ('发件箱与已发送', '已发送列表、发送状态与历史', iteration_ids[1], 'completed'),
        ('草稿箱', '草稿保存、自动保存、继续编辑', iteration_ids[1], 'completed'),
        ('定时发送与模板', '定时发送、邮件模板、紧急标记', iteration_ids[1], 'completed'),
        ('标签与分类', '自定义文件夹、星标、红旗/跟进标记', iteration_ids[2], 'completed'),
        ('账号与同步', '多账号、同步策略、服务器设置', iteration_ids[2], 'completed'),
        ('通知与显示', '新消息提醒、启动检查、显示设置', iteration_ids[2], 'completed'),
        ('搜索', '全文搜索、发件人/主题/关键词', iteration_ids[3], 'in_progress'),
        ('过滤与规则', '过滤规则、黑名单/白名单、反垃圾', iteration_ids[3], 'in_progress'),
        ('已读回执与撤回', '已读回执、邮件撤回', iteration_ids[3], 'in_progress'),
        ('多账号切换', '账号切换、发件人昵称与别名', iteration_ids[4], 'new'),
        ('推送与省电', '推送策略、省电模式下的同步', iteration_ids[4], 'new'),
        ('专项-性能', '大批量邮件、长列表滚动性能', iteration_ids[5], 'new'),
        ('专项-兼容', '多机型、多系统版本兼容', iteration_ids[5], 'new'),
    ]
    requirement_ids = []
    req_priorities = ['P0', 'P1', 'P2', 'P3', 'P4']
    for idx, (mod_name, desc, iter_id, status) in enumerate(req_rows):
        priority = req_priorities[idx % len(req_priorities)]
        cursor.execute("""
            INSERT INTO version_requirements (requirement_name, requirement_description, module, status, project_id, iteration_id, priority, estimated_hours, actual_hours, created_by, assigned_to, start_date, end_date, environment, is_deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f'需求-{mod_name}', desc, mod_name, status, project_id, iter_id, priority,
            12.0 + (idx % 5) * 2, 10.0, uid_creator, uid_tester1,
            (now - timedelta(days=90)).strftime(time_fmt), (now + timedelta(days=30)).strftime(time_fmt),
            'test', False,
        ))
        requirement_ids.append(cursor.lastrowid)

    print("插入用例库（邮箱功能模块 - 多层目录 + 多用例集）...")

    def _mk_folder(name, desc, parent_id, sort=0):
        cursor.execute("""
            INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
            VALUES (%s, %s, %s, 'folder', %s, %s, NULL, NULL, %s)
        """, (name, desc, parent_id, uid_creator, project_id, sort))
        return cursor.lastrowid

    def _mk_suite(name, desc, parent_id, req_id, iter_id, sort=0):
        cursor.execute("""
            INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
            VALUES (%s, %s, %s, 'suite', %s, %s, %s, %s, %s)
        """, (name, desc, parent_id, uid_creator, project_id, req_id, iter_id, sort))
        return cursor.lastrowid

    root_folder_id = _mk_folder('WPS邮箱用例库', '按邮箱功能模块划分', None)

    # ── 第一大类：邮件收发（二级目录，下含子目录 + 用例集）──
    f_send_recv = _mk_folder('邮件收发', '写邮件、收件、发件相关', root_folder_id, 0)
    f_compose = _mk_folder('写邮件与发信', '新建邮件、编辑、发送', f_send_recv, 0)
    f_attachment = _mk_folder('附件与签名', '附件添加、签名管理', f_send_recv, 1)
    f_inbox = _mk_folder('收件箱与阅读', '邮件列表、阅读、标记已读', f_send_recv, 2)
    f_sent = _mk_folder('发件箱与已发送', '已发送邮件管理', f_send_recv, 3)
    f_draft = _mk_folder('草稿箱', '草稿保存与恢复', f_send_recv, 4)
    f_schedule = _mk_folder('定时发送与模板', '定时发送、模板管理', f_send_recv, 5)

    # ── 第二大类：邮件管理（二级目录）──
    f_manage = _mk_folder('邮件管理', '标签、搜索、过滤、回执', root_folder_id, 1)
    f_label = _mk_folder('标签与分类', '标签管理、自动分类', f_manage, 0)
    f_search = _mk_folder('搜索', '关键字、高级搜索', f_manage, 1)
    f_filter = _mk_folder('过滤与规则', '自定义过滤规则', f_manage, 2)
    f_receipt = _mk_folder('已读回执与撤回', '回执请求、邮件撤回', f_manage, 3)

    # ── 第三大类：账号与系统（二级目录）──
    f_system = _mk_folder('账号与系统', '账号同步、通知、多账号', root_folder_id, 2)
    f_account = _mk_folder('账号与同步', 'IMAP/POP3 同步设置', f_system, 0)
    f_notify = _mk_folder('通知与显示', '推送通知、显示设置', f_system, 1)
    f_multi = _mk_folder('多账号切换', '多账号登录与切换', f_system, 2)

    # ── 第四大类：专项测试（根级同级目录，无子目录）──
    f_special = _mk_folder('专项测试', '性能、兼容、稳定性', root_folder_id, 3)

    MODULES = [
        ('写邮件与发信', requirement_ids[0], 28),
        ('附件与签名', requirement_ids[1], 18),
        ('收件箱与阅读', requirement_ids[2], 25),
        ('发件箱与已发送', requirement_ids[3], 12),
        ('草稿箱', requirement_ids[4], 14),
        ('定时发送与模板', requirement_ids[5], 16),
        ('标签与分类', requirement_ids[6], 22),
        ('账号与同步', requirement_ids[7], 20),
        ('通知与显示', requirement_ids[8], 15),
        ('搜索', requirement_ids[9], 20),
        ('过滤与规则', requirement_ids[10], 18),
        ('已读回执与撤回', requirement_ids[11], 10),
        ('多账号切换', requirement_ids[12], 14),
        ('专项-性能与兼容', requirement_ids[14], 25),
    ]

    folder_map = {
        '写邮件与发信': f_compose, '附件与签名': f_attachment,
        '收件箱与阅读': f_inbox, '发件箱与已发送': f_sent,
        '草稿箱': f_draft, '定时发送与模板': f_schedule,
        '标签与分类': f_label, '搜索': f_search,
        '过滤与规则': f_filter, '已读回执与撤回': f_receipt,
        '账号与同步': f_account, '通知与显示': f_notify,
        '多账号切换': f_multi, '专项-性能与兼容': f_special,
    }

    # 部分目录下创建多个用例集
    extra_suites_config = {
        '写邮件与发信': ['基本发信用例集', '编辑格式用例集', '发信异常用例集'],
        '收件箱与阅读': ['邮件列表用例集', '阅读操作用例集'],
        '标签与分类': ['标签管理用例集', '自动分类用例集'],
        '搜索': ['关键字搜索用例集', '高级搜索用例集'],
        '账号与同步': ['同步设置用例集', '多协议用例集'],
    }

    suite_rows = []
    for idx, (mod_name, req_id, case_count) in enumerate(MODULES):
        parent_fid = folder_map.get(mod_name, root_folder_id)
        iter_id = iteration_ids[idx % len(iteration_ids)]

        if mod_name in extra_suites_config:
            names = extra_suites_config[mod_name]
            per_count = max(1, case_count // len(names))
            for si, sname in enumerate(names):
                sid = _mk_suite(sname, f'{mod_name} - {sname}', parent_fid, req_id, iter_id, si)
                suite_rows.append((sid, project_id, req_id, mod_name, per_count if si < len(names) - 1 else case_count - per_count * (len(names) - 1)))
        else:
            sid = _mk_suite(f'{mod_name}用例集', f'{mod_name} 相关用例', parent_fid, req_id, iter_id, 0)
            suite_rows.append((sid, project_id, req_id, mod_name, case_count))

    print("插入测试用例（真实 WPS 邮箱场景）...")
    # 每个模块的真实用例：(场景分组, [(用例名, 测试数据, 前置条件, 操作步骤, 预期结果, 优先级)])
    WPS_CASES = {
        '写邮件与发信': [
            ('基本发信', [
                ('新建纯文本邮件并发送', '收件人: test@wps.cn', '已登录WPS邮箱且网络正常', '点击写邮件，填写收件人、主题和纯文本正文，点击发送', '邮件发送成功，已发送列表出现该邮件', 'P0'),
                ('新建富文本邮件并发送', '正文含加粗、斜体、超链接', '已登录', '新建邮件，使用富文本编辑器添加格式化内容后发送', '收件人收到邮件，格式正确显示', 'P0'),
                ('添加多个收件人发送', '收件人A、收件人B、收件人C', '已登录', '写邮件时在收件人栏依次输入3个邮箱地址，发送', '3个收件人均收到邮件', 'P0'),
                ('添加抄送和密送发送', 'CC: cc@wps.cn, BCC: bcc@wps.cn', '已登录', '展开CC/BCC栏，分别填入抄送和密送地址后发送', '抄送人可见邮件，密送人收到但不显示在收件人列表', 'P1'),
                ('发送空主题邮件', '主题为空', '已登录', '不填写主题直接点击发送', '弹出确认提示"主题为空，是否继续发送"', 'P1'),
                ('发送空正文邮件', '正文为空', '已登录', '只填写收件人和主题，正文留空，点击发送', '弹出确认提示或直接发送成功', 'P2'),
                ('收件人地址格式校验', '收件人: invalid-email', '已登录', '在收件人栏输入无效邮箱格式，点击发送', '提示"邮箱地址格式不正确"', 'P1'),
                ('发送超长正文邮件', '正文10000字', '已登录', '在正文中粘贴10000字内容后发送', '邮件发送成功，收件人完整收到全部内容', 'P2'),
            ]),
            ('编辑与格式', [
                ('正文插入图片', '本地图片1张', '已登录，新建邮件', '点击插入图片按钮，选择本地图片插入正文', '图片成功嵌入正文并可预览', 'P1'),
                ('正文插入表格', '3行3列表格', '已登录，新建邮件', '点击插入表格，创建3×3表格并填入数据', '表格正常显示，发送后收件人可见', 'P2'),
                ('撤销与重做操作', None, '已登录，正在编辑邮件', '输入文字后按Ctrl+Z撤销，再按Ctrl+Y重做', '撤销恢复到上一步，重做恢复撤销前状态', 'P2'),
                ('正文字体大小调整', None, '已登录，新建邮件', '选中文字，从字号下拉框选择18号字体', '选中文字字号变为18号', 'P2'),
                ('正文文字颜色设置', None, '已登录，新建邮件', '选中文字，点击字体颜色选红色', '选中文字颜色变为红色', 'P3'),
                ('复制粘贴外部内容', '从Word复制带格式文本', '已登录，新建邮件', '从Word文档复制带格式内容粘贴到邮件正文', '格式基本保留，不出现乱码', 'P2'),
            ]),
            ('异常场景', [
                ('网络断开时发送邮件', None, '已登录，邮件已编写完成', '断开网络后点击发送', '提示网络异常，邮件自动保存到发件箱或草稿箱', 'P1'),
                ('发送过程中切换账号', None, '已登录多账号', '邮件发送过程中切换到另一个账号', '发送任务不受影响，切换后可查看发送状态', 'P2'),
                ('发送超大邮件(50MB)', '正文+附件共50MB', '已登录', '编写含大量图片的邮件使总大小接近50MB后发送', '提示超过大小限制或发送成功（取决于服务器配置）', 'P2'),
                ('快速连续点击发送按钮', None, '已登录，邮件已编写', '快速连续点击3次发送按钮', '只发送1封邮件，不重复发送', 'P1'),
            ]),
        ],
        '附件与签名': [
            ('附件管理', [
                ('添加单个小附件', '文件: test.pdf (100KB)', '已登录，新建邮件', '点击添加附件，选择100KB的PDF文件', '附件添加成功，显示文件名和大小', 'P0'),
                ('添加多个附件', '3个文件共5MB', '已登录，新建邮件', '依次添加3个不同类型文件（PDF/DOC/JPG）', '3个附件全部显示在附件栏', 'P0'),
                ('添加超大附件(25MB)', '文件: large.zip (25MB)', '已登录，新建邮件', '添加25MB的压缩文件作为附件', '提示附件过大或上传成功（取决于限制配置）', 'P1'),
                ('删除已添加的附件', None, '已添加2个附件', '点击其中一个附件的删除按钮', '该附件被移除，另一个附件保留', 'P1'),
                ('附件预览功能', '文件: preview.pdf', '已添加PDF附件', '点击附件的预览按钮', '弹出预览窗口，可查看PDF内容', 'P2'),
                ('添加同名附件', '两个同名文件test.txt', '已登录，新建邮件', '添加test.txt后再次添加同名文件', '提示文件重复或自动重命名', 'P2'),
                ('拖拽添加附件', '桌面文件', '已登录，新建邮件', '从桌面拖拽文件到邮件编辑区域', '附件添加成功', 'P2'),
            ]),
            ('签名管理', [
                ('创建文本签名', '签名内容: 张三-测试部', '已登录，进入签名设置', '点击新建签名，输入纯文本内容，保存', '签名创建成功，列表中显示新签名', 'P0'),
                ('创建富文本签名', '签名含图片和链接', '已登录，进入签名设置', '新建签名，添加公司Logo图片和官网链接', '签名保存成功，预览显示正确', 'P1'),
                ('设置默认签名', None, '已创建多个签名', '选择一个签名设为默认', '新建邮件时自动带入该签名', 'P1'),
                ('编辑已有签名', None, '已有签名', '修改签名内容并保存', '签名更新成功，新邮件使用更新后的签名', 'P2'),
                ('删除签名', None, '已有多个签名', '删除其中一个非默认签名', '签名删除成功，默认签名不受影响', 'P2'),
                ('写邮件时切换签名', None, '已创建多个签名，正在写邮件', '点击签名切换按钮，选择另一个签名', '邮件底部签名切换为所选签名', 'P2'),
            ]),
        ],
        '收件箱与阅读': [
            ('收件箱列表', [
                ('查看收件箱邮件列表', None, '已登录，收件箱有邮件', '点击收件箱', '显示邮件列表，包含发件人、主题、时间、未读标记', 'P0'),
                ('收件箱下拉刷新', None, '已登录', '在收件箱列表下拉刷新', '触发同步，显示最新邮件', 'P0'),
                ('未读邮件高亮显示', None, '收件箱有未读邮件', '查看收件箱列表', '未读邮件标题加粗或有未读标记，已读邮件正常显示', 'P0'),
                ('收件箱分页加载', None, '收件箱有100+封邮件', '滚动到列表底部', '自动加载下一页邮件，无重复', 'P1'),
                ('按时间排序', None, '收件箱有多封邮件', '点击按时间排序', '邮件按接收时间降序排列', 'P1'),
                ('收件箱显示附件图标', None, '有带附件的邮件', '查看收件箱列表', '带附件的邮件显示附件图标', 'P2'),
            ]),
            ('邮件阅读', [
                ('打开并阅读邮件', None, '收件箱有未读邮件', '点击一封未读邮件', '打开邮件详情，显示发件人、时间、主题、正文，标记为已读', 'P0'),
                ('阅读带附件的邮件', None, '有带附件的邮件', '打开带附件的邮件', '正文正常显示，附件列表显示文件名和大小', 'P0'),
                ('阅读富文本邮件', None, '有富文本格式邮件', '打开富文本邮件', '加粗、斜体、颜色、图片等格式正确渲染', 'P1'),
                ('邮件内链接点击', None, '邮件正文含超链接', '点击正文中的超链接', '在浏览器中打开对应链接', 'P2'),
                ('长邮件滚动阅读', None, '有超长正文的邮件', '打开并向下滚动', '滚动流畅，内容完整加载', 'P2'),
            ]),
            ('邮件操作', [
                ('回复邮件', None, '已打开一封邮件', '点击回复按钮，输入回复内容，发送', '回复成功，原始邮件引用在下方', 'P0'),
                ('全部回复', None, '打开一封多人邮件', '点击全部回复，输入内容发送', '所有收件人和抄送人均收到回复', 'P1'),
                ('转发邮件', None, '已打开一封邮件', '点击转发，填入新收件人，发送', '新收件人收到转发邮件，含原始内容', 'P0'),
                ('标记邮件为未读', None, '已读邮件', '右键选择"标记为未读"', '邮件恢复未读状态，列表中显示未读标记', 'P1'),
                ('星标/红旗标记邮件', None, '已打开邮件', '点击星标/红旗图标', '邮件被标记，可在星标文件夹中找到', 'P1'),
                ('删除邮件到回收站', None, '收件箱有邮件', '选中邮件点击删除', '邮件移至回收站，收件箱不再显示', 'P1'),
                ('批量删除邮件', None, '收件箱有多封邮件', '勾选多封邮件后点击批量删除', '所有选中邮件移至回收站', 'P2'),
                ('批量标记已读', None, '有多封未读邮件', '全选未读邮件，点击标记已读', '所有选中邮件变为已读状态', 'P2'),
            ]),
        ],
        '发件箱与已发送': [
            ('已发送管理', [
                ('查看已发送列表', None, '已发送过邮件', '点击已发送文件夹', '显示所有已发送邮件，含收件人、主题、发送时间', 'P0'),
                ('打开已发送邮件详情', None, '已发送列表有邮件', '点击一封已发送邮件', '显示邮件完整内容，包含收件人、抄送人、正文', 'P0'),
                ('重新发送已发送邮件', None, '已打开一封已发送邮件', '点击重新发送', '打开编辑页面，预填原邮件内容，可修改后发送', 'P1'),
                ('转发已发送邮件', None, '已打开已发送邮件', '点击转发，填写新收件人', '新收件人收到邮件', 'P1'),
                ('已发送列表搜索', '关键词: 周报', '已发送文件夹有邮件', '在搜索栏输入"周报"', '列表筛选出主题含"周报"的邮件', 'P2'),
                ('已发送邮件删除', None, '已发送列表有邮件', '选中邮件点击删除', '邮件从已发送列表移除', 'P2'),
            ]),
            ('发送状态', [
                ('查看发送中状态', None, '刚发送一封邮件', '查看发件箱', '显示"发送中"状态', 'P1'),
                ('查看发送失败邮件', None, '有发送失败的邮件', '查看发件箱', '显示失败标记和失败原因', 'P1'),
                ('重试发送失败的邮件', None, '发件箱有失败邮件', '点击重试按钮', '邮件重新发送', 'P1'),
                ('发件箱列表排序', None, '发件箱有多封邮件', '按时间排序', '按发送时间降序排列', 'P2'),
            ]),
        ],
        '草稿箱': [
            ('草稿基本操作', [
                ('手动保存草稿', None, '已登录，正在编写邮件', '点击保存草稿按钮', '邮件保存到草稿箱，提示保存成功', 'P0'),
                ('自动保存草稿', None, '已登录，正在编写邮件', '编写邮件内容后等待30秒不操作', '系统自动保存草稿', 'P0'),
                ('继续编辑草稿', None, '草稿箱有草稿', '点击打开草稿', '恢复编辑状态，收件人/主题/正文/附件均保留', 'P0'),
                ('草稿另存为模板', None, '草稿箱有草稿', '打开草稿，选择另存为模板', '模板保存成功', 'P2'),
                ('从草稿发送邮件', None, '草稿箱有完整草稿', '打开草稿点击发送', '邮件发送成功，草稿箱中该草稿消失', 'P0'),
            ]),
            ('草稿管理', [
                ('查看草稿箱列表', None, '草稿箱有草稿', '点击草稿箱', '显示所有草稿，含主题、最后修改时间', 'P0'),
                ('删除草稿', None, '草稿箱有草稿', '选中草稿点击删除', '草稿删除成功', 'P1'),
                ('批量删除草稿', None, '草稿箱有多个草稿', '全选后批量删除', '所有选中草稿被删除', 'P2'),
                ('草稿含附件继续编辑', '草稿含2个附件', '草稿箱有带附件的草稿', '打开草稿', '附件仍在，可继续添加或删除附件', 'P1'),
                ('编写中关闭页面自动保存', None, '正在编写邮件', '关闭浏览器标签页', '弹出提示是否保存，选择保存后草稿保留', 'P1'),
            ]),
        ],
        '定时发送与模板': [
            ('定时发送', [
                ('设置定时发送', '发送时间: 明天10:00', '已登录，邮件已编写完成', '点击定时发送，选择明天10:00', '邮件进入定时队列，到时自动发送', 'P0'),
                ('修改定时发送时间', None, '有待发送的定时邮件', '找到定时邮件，修改发送时间', '发送时间更新成功', 'P1'),
                ('取消定时发送', None, '有待发送的定时邮件', '点击取消定时发送', '邮件回到草稿箱', 'P1'),
                ('定时发送时间已过', '发送时间设为过去时间', '已登录', '设置定时发送时间为过去的时间', '提示时间无效或立即发送', 'P2'),
                ('查看定时发送列表', None, '有多封定时邮件', '进入定时发送文件夹', '显示所有待发送邮件和预定时间', 'P1'),
            ]),
            ('邮件模板', [
                ('创建邮件模板', '模板名: 周报模板', '已登录', '进入模板管理，新建模板，填写内容保存', '模板创建成功', 'P0'),
                ('使用模板写邮件', None, '已有模板', '写邮件时点击使用模板，选择周报模板', '邮件正文自动填入模板内容', 'P0'),
                ('编辑模板', None, '已有模板', '进入模板管理，选择模板编辑内容', '模板更新成功', 'P1'),
                ('删除模板', None, '已有多个模板', '选择一个模板删除', '模板删除成功', 'P2'),
                ('模板含变量占位符', '模板含 {日期} 占位符', '已创建含占位符的模板', '使用该模板写邮件', '占位符显示并可手动替换', 'P2'),
                ('紧急标记邮件', None, '已登录，写邮件', '勾选紧急/重要标记后发送', '收件人看到紧急标记', 'P1'),
            ]),
        ],
        '标签与分类': [
            ('文件夹管理', [
                ('创建自定义文件夹', '文件夹名: 项目邮件', '已登录', '在文件夹列表点击新建，输入名称', '文件夹创建成功，侧栏显示', 'P0'),
                ('重命名文件夹', None, '已有自定义文件夹', '右键选择重命名，输入新名称', '文件夹名称更新', 'P1'),
                ('删除自定义文件夹', None, '已有空的自定义文件夹', '右键删除文件夹', '文件夹删除成功', 'P1'),
                ('删除含邮件的文件夹', None, '文件夹内有邮件', '右键删除文件夹', '提示邮件将移至回收站，确认后删除', 'P1'),
                ('移动邮件到文件夹', None, '收件箱有邮件，已创建文件夹', '拖拽或右键移动邮件到自定义文件夹', '邮件出现在目标文件夹中', 'P0'),
                ('批量移动邮件', None, '收件箱有多封邮件', '选中多封邮件，批量移动到文件夹', '所有选中邮件移动成功', 'P2'),
            ]),
            ('标记功能', [
                ('给邮件添加星标', None, '收件箱有邮件', '点击邮件旁的星标图标', '星标点亮，邮件出现在星标文件夹', 'P0'),
                ('取消星标', None, '已有星标邮件', '再次点击星标图标', '星标取消，邮件从星标文件夹消失', 'P1'),
                ('给邮件添加红旗标记', None, '收件箱有邮件', '右键选择红旗标记', '邮件显示红旗图标', 'P1'),
                ('给邮件添加跟进标记', None, '收件箱有邮件', '右键选择跟进标记', '邮件显示跟进标志，跟进列表中出现', 'P2'),
                ('按标记筛选邮件', None, '有不同标记的邮件', '点击筛选，选择星标邮件', '只显示有星标的邮件', 'P1'),
                ('批量添加标记', None, '选中多封邮件', '全选后批量添加星标', '所有选中邮件都添加星标', 'P2'),
            ]),
            ('颜色标签', [
                ('给邮件添加颜色标签', None, '收件箱有邮件', '右键选择颜色标签-红色', '邮件列表中显示红色标签标识', 'P2'),
                ('按颜色标签筛选', None, '有不同颜色标签的邮件', '选择按红色标签筛选', '只显示红色标签的邮件', 'P2'),
                ('修改邮件颜色标签', None, '已有红色标签的邮件', '右键修改标签为蓝色', '标签颜色更新为蓝色', 'P3'),
                ('删除邮件颜色标签', None, '已有颜色标签的邮件', '右键选择删除标签', '邮件标签移除', 'P3'),
            ]),
        ],
        '账号与同步': [
            ('账号管理', [
                ('添加邮箱账号(IMAP)', '服务器: imap.wps.cn', '已登录主账号', '进入设置-账号管理-添加账号，填写IMAP配置', '账号添加成功，开始同步邮件', 'P0'),
                ('添加邮箱账号(POP3)', '服务器: pop3.wps.cn', '已登录主账号', '添加POP3类型账号', '账号添加成功', 'P1'),
                ('添加Exchange账号', '服务器: exchange.company.com', '已登录主账号', '添加Exchange账号并配置', '账号添加成功，日历和联系人同步', 'P1'),
                ('删除邮箱账号', None, '已添加多个账号', '进入账号管理，选择一个账号删除', '账号删除成功，相关邮件数据清理', 'P1'),
                ('修改账号密码', None, '已有账号', '修改账号的登录密码', '密码更新成功，重新验证通过', 'P1'),
                ('账号信息编辑', '显示名: 张三', '已有账号', '修改账号的发件人显示名称', '下次发邮件时显示新名称', 'P2'),
            ]),
            ('同步设置', [
                ('手动同步邮件', None, '已登录', '点击同步按钮', '邮件开始同步，显示同步进度', 'P0'),
                ('设置自动同步频率', '频率: 每15分钟', '已登录', '进入设置，将自动同步频率设为15分钟', '设置保存成功，按设定频率自动同步', 'P1'),
                ('设置同步天数范围', '同步最近30天', '已登录', '设置只同步最近30天的邮件', '只下载30天内的邮件', 'P1'),
                ('仅Wi-Fi下同步', None, '已登录', '开启"仅在Wi-Fi下同步"', '移动数据下不自动同步', 'P2'),
                ('同步冲突处理', None, '多设备同时操作同一邮件', '在A设备删除邮件，B设备标星同一邮件后同步', '以最后操作为准或提示冲突', 'P2'),
                ('同步进度显示', None, '首次添加账号', '观察邮件同步过程', '显示同步进度条和已同步数量', 'P2'),
                ('同步失败重试', None, '同步过程中网络中断', '网络恢复后触发同步', '自动重试同步，不丢失数据', 'P1'),
            ]),
        ],
        '通知与显示': [
            ('通知设置', [
                ('开启新邮件通知', None, '已登录', '进入设置开启新邮件通知', '收到新邮件时弹出通知', 'P0'),
                ('关闭通知', None, '通知已开启', '关闭新邮件通知', '收到新邮件不再弹出通知', 'P1'),
                ('设置通知声音', '声音: 默认提示音', '已开启通知', '选择自定义通知声音', '新邮件到达时播放所选声音', 'P2'),
                ('设置免打扰时段', '22:00-08:00', '已开启通知', '设置22点到8点免打扰', '免打扰时段内不发送通知', 'P2'),
                ('VIP联系人通知', None, '已设置VIP联系人', '开启VIP联系人专属通知', '只有VIP发来的邮件触发通知', 'P2'),
                ('通知预览内容设置', None, '已开启通知', '设置通知只显示发件人不显示正文', '通知中只显示发件人名称', 'P3'),
            ]),
            ('显示设置', [
                ('切换邮件列表密度', None, '已登录', '切换列表显示为紧凑模式', '每行高度减小，单屏显示更多邮件', 'P1'),
                ('切换阅读面板位置', None, '已登录', '将阅读面板从右侧切换到底部', '阅读面板移至底部显示', 'P2'),
                ('邮件列表预览行数', '预览2行', '已登录', '设置邮件预览显示2行摘要', '列表中每封邮件显示2行正文预览', 'P2'),
                ('深色模式切换', None, '已登录', '在显示设置中开启深色模式', '界面切换为深色主题', 'P2'),
                ('字体大小调整', None, '已登录', '将邮件正文字体调大', '阅读邮件时正文字体变大', 'P3'),
                ('头像显示设置', None, '已登录', '开启发件人头像显示', '邮件列表显示发件人头像', 'P3'),
                ('会话模式切换', None, '已登录', '开启会话/聚合模式', '相同主题的邮件聚合为一组显示', 'P1'),
            ]),
        ],
        '搜索': [
            ('基本搜索', [
                ('按关键词搜索', '关键词: 项目进度', '已登录，有邮件数据', '在搜索栏输入"项目进度"回车', '列出主题或正文含"项目进度"的邮件', 'P0'),
                ('按发件人搜索', '发件人: zhangsan@wps.cn', '已登录', '在搜索栏输入发件人邮箱', '列出该发件人的所有邮件', 'P0'),
                ('按主题搜索', '主题: 周报', '已登录', '选择按主题搜索，输入"周报"', '只搜索主题字段匹配的邮件', 'P1'),
                ('按收件人搜索', '收件人: team@wps.cn', '已登录', '选择按收件人搜索', '列出发给该地址的邮件', 'P1'),
                ('搜索无结果', '关键词: xyzabc123', '已登录', '搜索不存在的关键词', '显示无搜索结果提示', 'P2'),
                ('清除搜索条件', None, '已有搜索结果', '点击清除按钮', '搜索条件清空，恢复正常邮件列表', 'P2'),
            ]),
            ('高级搜索', [
                ('按日期范围搜索', '日期: 2024-01-01至2024-01-31', '已登录', '设置日期范围后搜索', '只显示该时间范围内的邮件', 'P1'),
                ('按是否有附件搜索', None, '已登录', '勾选"有附件"筛选条件', '只显示包含附件的邮件', 'P1'),
                ('按未读状态搜索', None, '已登录', '勾选"仅未读"筛选', '只显示未读邮件', 'P2'),
                ('按文件夹范围搜索', None, '已登录', '选择只在收件箱中搜索', '搜索范围限定在收件箱', 'P2'),
                ('组合条件搜索', '发件人+日期+关键词', '已登录', '同时设置发件人、日期范围和关键词', '返回满足所有条件的邮件', 'P1'),
                ('搜索结果排序', None, '有搜索结果', '按相关度/时间切换排序', '搜索结果按选择的方式重新排序', 'P2'),
                ('搜索历史记录', None, '已搜索过', '点击搜索栏', '显示最近搜索记录', 'P3'),
            ]),
        ],
        '过滤与规则': [
            ('过滤规则', [
                ('创建过滤规则-按发件人', '规则: zhangsan发来的→移到项目文件夹', '已登录', '新建规则：发件人含zhangsan时自动移到指定文件夹', '规则创建成功', 'P0'),
                ('创建过滤规则-按主题', '规则: 主题含"发票"→标记重要', '已登录', '新建规则：主题含关键词时自动标记', '规则创建成功', 'P1'),
                ('编辑已有规则', None, '已有过滤规则', '修改规则条件或动作', '规则更新成功', 'P1'),
                ('删除过滤规则', None, '已有规则', '删除一条规则', '规则删除成功', 'P1'),
                ('启用/禁用规则', None, '已有规则', '切换规则的启用状态', '禁用后规则不再自动执行', 'P1'),
                ('规则优先级排序', None, '已有多条规则', '拖拽调整规则顺序', '规则按新顺序执行', 'P2'),
                ('规则冲突处理', '两条规则针对同一邮件', '已有冲突规则', '收到符合两条规则的邮件', '按规则优先级执行第一条匹配规则', 'P2'),
                ('对已有邮件应用规则', None, '已有规则和邮件', '选择对收件箱已有邮件应用规则', '已有邮件按规则自动分类', 'P2'),
            ]),
            ('黑白名单', [
                ('添加黑名单', '邮箱: spam@test.com', '已登录', '将地址添加到黑名单', '该地址来信自动进入垃圾箱', 'P0'),
                ('添加白名单', '邮箱: vip@partner.com', '已登录', '将地址添加到白名单', '该地址来信不被误判为垃圾邮件', 'P1'),
                ('从黑名单移除', None, '黑名单有地址', '移除一个黑名单地址', '该地址来信恢复正常收取', 'P1'),
                ('黑名单批量导入', '10个邮箱地址列表', '已登录', '批量导入黑名单地址', '所有地址添加成功', 'P2'),
                ('举报垃圾邮件', None, '收到垃圾邮件', '点击举报按钮', '邮件移至垃圾箱，发件人自动加入黑名单', 'P1'),
            ]),
        ],
        '已读回执与撤回': [
            ('已读回执', [
                ('发送带已读回执的邮件', None, '已登录', '写邮件时勾选"请求已读回执"后发送', '邮件发送成功，等待对方确认', 'P0'),
                ('收到已读回执请求', None, '收到请求回执的邮件', '打开邮件', '弹出是否发送已读回执的确认框', 'P0'),
                ('同意发送已读回执', None, '弹出确认框', '点击同意', '回执发送给发件人', 'P1'),
                ('拒绝发送已读回执', None, '弹出确认框', '点击拒绝', '不发送回执，正常阅读邮件', 'P1'),
                ('查看已读回执状态', None, '已发送带回执的邮件', '打开已发送邮件查看回执状态', '显示已读/未读状态和时间', 'P1'),
            ]),
            ('邮件撤回', [
                ('撤回刚发送的邮件', None, '刚发送一封邮件（60秒内）', '点击撤回按钮', '邮件从收件人邮箱撤回成功', 'P0'),
                ('超时后尝试撤回', None, '发送超过2分钟的邮件', '尝试撤回', '提示已超过撤回时限', 'P1'),
                ('撤回后邮件状态', None, '已成功撤回邮件', '查看已发送列表', '显示"已撤回"状态标记', 'P1'),
                ('收件人已读后撤回', None, '收件人已读邮件', '发件人尝试撤回', '提示对方已读，撤回可能失败', 'P2'),
                ('撤回带附件的邮件', None, '刚发送带附件邮件', '立即撤回', '邮件和附件均被撤回', 'P2'),
            ]),
        ],
        '多账号切换': [
            ('账号切换', [
                ('切换到另一个账号', None, '已添加2个以上账号', '点击账号切换器，选择另一个账号', '邮箱切换到所选账号的收件箱', 'P0'),
                ('切换后收件箱数据正确', None, '切换到账号B', '查看收件箱', '显示账号B的邮件，非账号A的', 'P0'),
                ('切换账号后发邮件', None, '当前为账号B', '写邮件发送', '邮件从账号B发出', 'P0'),
                ('快速切换频繁操作', None, '已有多个账号', '连续快速切换5次', '界面正常，数据不混乱', 'P1'),
                ('统一收件箱模式', None, '已有多个账号', '开启统一收件箱', '所有账号邮件合并显示在一个列表中', 'P1'),
                ('统一收件箱区分来源', None, '统一收件箱模式开启', '查看合并列表', '每封邮件标识其来源账号', 'P2'),
            ]),
            ('别名与昵称', [
                ('设置发件人别名', '别名: support@company.com', '已登录', '在账号设置中添加别名邮箱', '别名添加成功', 'P1'),
                ('使用别名发信', None, '已设置别名', '写邮件时切换发件人为别名', '邮件以别名地址发出', 'P1'),
                ('修改发件人昵称', '昵称: 张三（技术部）', '已登录', '修改发件人显示昵称', '发送邮件时显示新昵称', 'P2'),
                ('默认发件账号设置', None, '已有多个账号', '设置默认发件账号', '新建邮件默认使用该账号', 'P2'),
            ]),
        ],
        '专项-性能与兼容': [
            ('性能测试', [
                ('大量邮件列表加载(1000+)', '收件箱1000+封', '已登录，大量邮件', '打开收件箱，滚动浏览', '列表加载流畅，滚动无卡顿', 'P0'),
                ('大量邮件搜索性能', '搜索范围: 全部邮件5000+封', '已登录', '全文搜索常用关键词', '3秒内返回搜索结果', 'P0'),
                ('大附件上传性能', '附件: 20MB视频文件', '已登录', '上传20MB附件', '上传进度正常显示，无超时', 'P1'),
                ('同时打开多封邮件', None, '已登录', '同时打开10封邮件', '每封邮件正常加载，内存占用合理', 'P1'),
                ('长时间运行稳定性', None, '已登录', '客户端连续运行8小时', '无崩溃、无内存泄漏', 'P1'),
                ('批量操作性能', '选中100封邮件', '收件箱100+封邮件', '全选100封邮件后批量删除', '操作响应时间<2秒', 'P2'),
                ('离线缓存加载速度', None, '之前已同步邮件', '断网后打开邮箱', '已缓存邮件秒级加载', 'P2'),
                ('首次启动加载速度', None, '全新安装', '首次启动应用并登录', '首页加载时间<3秒', 'P1'),
            ]),
            ('兼容性测试', [
                ('Android 10 兼容', '设备: Android 10', 'Android 10 设备', '安装并使用全部核心功能', '功能正常，UI适配', 'P0'),
                ('Android 12 兼容', '设备: Android 12', 'Android 12 设备', '安装并使用全部核心功能', '功能正常', 'P0'),
                ('Android 14 兼容', '设备: Android 14', 'Android 14 设备', '安装并使用全部核心功能', '功能正常', 'P0'),
                ('iOS 15 兼容', '设备: iOS 15', 'iOS 15 设备', '安装并使用全部核心功能', '功能正常', 'P0'),
                ('iOS 17 兼容', '设备: iOS 17', 'iOS 17 设备', '安装并使用全部核心功能', '功能正常', 'P0'),
                ('平板适配', '设备: iPad', 'iPad设备', '横屏和竖屏使用全部功能', 'UI适配良好，无变形', 'P1'),
                ('小屏手机适配', '屏幕: 5寸720p', '小屏手机', '使用全部核心功能', 'UI正常，文字不截断', 'P1'),
                ('暗色模式兼容', None, '系统开启暗色模式', '检查所有页面', '所有页面适配暗色模式，无白屏', 'P1'),
                ('横竖屏切换', None, '已登录', '阅读邮件时旋转屏幕', '内容自适应，不丢失数据', 'P2'),
                ('多语言环境', '系统语言: English', '系统设为英语', '使用邮箱全部功能', '界面文字显示英文，无乱码', 'P2'),
                ('低内存设备', '设备: 2GB RAM', '低配设备', '正常使用邮箱', '可正常运行，不频繁闪退', 'P2'),
            ]),
        ],
    }

    cases_data = []
    case_seq = 0
    cases_by_suite = {}
    for suite_id, proj_id, req_id, mod_name, _n in suite_rows:
        module_cases = WPS_CASES.get(mod_name, {})
        iter_id = iteration_ids[0]
        suite_cases = []
        for _group_name, group_cases in (module_cases if isinstance(module_cases, list) else module_cases.items()):
            group_list = group_cases if isinstance(group_cases, list) else _group_name
            if isinstance(_group_name, str) and isinstance(group_cases, list):
                for c in group_cases:
                    case_seq += 1
                    cname, td, pre, step, er, pri = c
                    case_number = f"TC-WPS-{case_seq:04d}"
                    suite_cases.append((case_number, cname, td, pre, step, er, pri))
                    cases_data.append((
                        case_number, cname, f'{mod_name} - {_group_name}', pri, uid_tester1,
                        proj_id, req_id, iter_id, suite_id,
                        pre, step, er, None, td,
                        uid_tester1, uid_reviewer,
                    ))
        cases_by_suite[suite_id] = suite_cases

    cursor.executemany("""
        INSERT INTO test_cases (case_number, case_name, case_description, priority, creator_id,
            project_id, version_requirement_id, iteration_id, suite_id,
            preconditions, steps, expected_result, actual_result, test_data,
            assignee_id, reviewer_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, cases_data)
    print(f"  共插入 {len(cases_data)} 条用例")

    cursor.execute("SELECT id, suite_id, case_number FROM test_cases ORDER BY id")
    case_suite_map = {}
    case_id_by_number = {}
    for cid, sid, cnum in cursor.fetchall():
        case_suite_map.setdefault(sid, []).append(cid)
        case_id_by_number[cnum] = cid

    # ---------- 为每个用例集生成脑图 JSON（多样化链深度）并回写 ----------
    print("生成脑图数据并回写...")
    for suite_id, proj_id, req_id, mod_name, _n in suite_rows:
        module_cases = WPS_CASES.get(mod_name, {})
        if not module_cases:
            continue

        root_children = []
        case_idx = 0
        for group_name, group_cases in (module_cases if isinstance(module_cases, list) else module_cases.items()):
            if not isinstance(group_name, str):
                continue
            group_id = f'g-{suite_id}-{case_idx}'
            case_nodes = []
            for ci, c in enumerate(group_cases):
                cname, td, pre, step, er, pri = c
                case_idx += 1
                node_id = f'c-{suite_id}-{case_idx}'
                case_number = None
                for sc in cases_by_suite.get(suite_id, []):
                    if sc[1] == cname:
                        case_number = sc[0]
                        break
                db_id = case_id_by_number.get(case_number)
                if db_id:
                    cursor.execute("UPDATE test_cases SET mindmap_node_id=%s, group_path=%s WHERE id=%s",
                                   (node_id, group_name, db_id))

                # 用例链完整：(test_data →) precondition → step → expected_result
                # test_data 可选，取决于原始数据是否有 td
                sid_ci = f'{suite_id}-{case_idx}'
                er_node = {'id': f'er-{sid_ci}', 'text': er, 'attribute': 'expected_result'}
                st_node = {'id': f'st-{sid_ci}', 'text': step, 'attribute': 'step', 'children': [er_node]}
                pc_node = {'id': f'pc-{sid_ci}', 'text': pre, 'attribute': 'precondition', 'children': [st_node]}
                if td:
                    chain = [{'id': f'td-{sid_ci}', 'text': td, 'attribute': 'test_data', 'children': [pc_node]}]
                else:
                    chain = [pc_node]

                case_nodes.append({
                    'id': node_id, 'text': cname, 'attribute': 'case_title', 'priority': pri, 'children': chain,
                })

            root_children.append({'id': group_id, 'text': group_name, 'children': case_nodes})

        total = sum(len(gc) for _, gc in module_cases.items()) if isinstance(module_cases, dict) else 0
        mindmap_json = json.dumps({
            'version': '2.0',
            'root': {'id': 'root', 'text': f'{mod_name}用例集', 'children': root_children},
            'metadata': {'total_cases': total, 'last_saved_at': now.strftime(time_fmt), 'last_saved_by': uid_creator},
        }, ensure_ascii=False)

        review_st = ['not_reviewed', 'pending', 'completed'][suite_id % 3]
        edit_st = 'completed' if review_st == 'completed' else 'drafting'
        cursor.execute(
            "UPDATE test_suites SET case_mindmap_data=%s, case_count=%s, "
            "review_status=%s, case_edit_status=%s, last_saved_at=%s, last_saved_by=%s WHERE id=%s",
            (mindmap_json, total, review_st, edit_st, now.strftime(time_fmt), uid_creator, suite_id))

    # ---------- 插入标签和标记字典 ----------
    print("插入标签和标记...")
    tag_data = [
        ('冒烟测试', '#67C23A', project_id, uid_creator),
        ('回归测试', '#E6A23C', project_id, uid_creator),
        ('核心用例', '#F56C6C', project_id, uid_creator),
        ('自动化', '#409EFF', project_id, uid_creator),
        ('体验优化', '#909399', project_id, uid_creator),
    ]
    cursor.executemany(
        "INSERT INTO case_tags (tag_name, tag_color, project_id, creator_id) VALUES (%s,%s,%s,%s)",
        tag_data)
    marker_data = [
        ('system', project_id, uid_creator),
        ('system', project_id, uid_creator),
        ('system', project_id, uid_creator),
        ('custom', project_id, uid_creator),
    ]
    marker_names = ['未完成', '待确认', '待修改', '需讨论']
    for i, (mt, pid, cid) in enumerate(marker_data):
        cursor.execute(
            "INSERT INTO case_markers (marker_name, marker_type, project_id, creator_id) VALUES (%s,%s,%s,%s)",
            (marker_names[i], mt, pid, cid))

    print("插入用例评审与评审历史...")
    review_statuses = ['pending', 'in_review', 'completed', 'rejected']
    suite_ids_all = [r[0] for r in suite_rows]
    review_task_count = 0
    for initiator_id in user_ids:
        for reviewer_id in user_ids:
            if initiator_id == reviewer_id:
                continue
            for si, suite_id in enumerate(suite_ids_all):
                if review_task_count >= 80:
                    break
                status = review_statuses[(initiator_id + reviewer_id + si) % 4]
                start_t = (now - timedelta(days=10 + si % 5)).strftime(time_fmt)
                end_t = (now - timedelta(days=9 + si % 5)).strftime(time_fmt) if status in ('completed', 'rejected') else None
                comments = '用例覆盖完整，通过评审。' if status == 'completed' else ('请修改后重新提交。' if status == 'rejected' else None)
                cursor.execute("""
                    INSERT INTO test_suite_review_tasks (suite_id, initiator_id, reviewer_id, status, start_time, end_time, overall_comments)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (suite_id, initiator_id, reviewer_id, status, start_t, end_t, comments))
                rt_id = cursor.lastrowid
                review_task_count += 1
                case_ids = case_suite_map.get(suite_id, [])
                for case_id in case_ids[:25]:
                    rev_status = 'approved' if status == 'completed' else ('rejected' if status == 'rejected' else 'pending')
                    cursor.execute("""
                        INSERT INTO test_case_review_details (review_task_id, case_id, reviewer_id, review_status, comments)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (rt_id, case_id, reviewer_id, rev_status, '通过' if rev_status == 'approved' else (None if rev_status == 'pending' else '需修改')))
                if status in ('completed', 'rejected'):
                    hist_rev_status = 'approved' if status == 'completed' else 'rejected'
                    cursor.execute("""
                        INSERT INTO test_suite_review_history (review_task_id, suite_id, initiator_id, reviewer_id, status, start_time, end_time, overall_comments, history_type, created_by, version)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (rt_id, suite_id, initiator_id, reviewer_id, status, start_t, end_t, comments, 'complete' if status == 'completed' else 'reject', reviewer_id, 1))
                    history_id = cursor.lastrowid
                    for case_id in case_ids[:20]:
                        cursor.execute("SELECT case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result FROM test_cases WHERE id = %s", (case_id,))
                        row = cursor.fetchone()
                        if not row:
                            continue
                        cursor.execute("""
                            INSERT INTO test_case_review_history (review_history_id, review_task_id, case_id, reviewer_id, review_status, comments, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result, created_by)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (history_id, rt_id, case_id, reviewer_id, hist_rev_status, '通过' if hist_rev_status == 'approved' else None, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], reviewer_id))
        if review_task_count >= 80:
            break

    print("插入任务文件夹...")
    folder_data = [
        ('写邮件与发信', None, 'test_case', 0),
        ('收件箱与阅读', None, 'test_case', 1),
        ('发件箱与草稿', None, 'test_case', 2),
        ('标签与搜索', None, 'test_case', 3),
        ('账号与同步', None, 'test_case', 4),
        ('通知与设置', None, 'test_case', 5),
        ('专项测试', None, 'test_case', 6),
        ('设备巡检', None, 'device_script', 0),
        ('获取设备信息', None, 'device_script', 1),
    ]
    for name, parent_id, task_type, sort_order in folder_data:
        cursor.execute("INSERT INTO task_folders (name, parent_id, task_type, sort_order) VALUES (%s, %s, %s, %s)", (name, parent_id, task_type, sort_order))
    cursor.execute("SELECT id FROM task_folders WHERE task_type = 'test_case' ORDER BY sort_order")
    folder_tc = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM task_folders WHERE task_type = 'device_script' ORDER BY sort_order")
    folder_ds = [row[0] for row in cursor.fetchall()]

    print("插入测试任务...")
    suite_id_to_name = {r[0]: r[3] for r in suite_rows}
    tasks_data = []
    for idx, row in enumerate(suite_rows):
        suite_id, proj_id, req_id, mod_name, _ = row
        status = ['pending', 'running', 'completed'][idx % 3]
        executor_id = user_ids[idx % len(user_ids)] if status in ('completed', 'running') else None
        scheduled_start = (now - timedelta(days=3)).strftime(time_fmt)
        scheduled_end = (now + timedelta(days=1)).strftime(time_fmt)
        started_time = (now - timedelta(hours=2)).strftime(time_fmt) if status != 'pending' else None
        completed_time = (now - timedelta(minutes=30)).strftime(time_fmt) if status == 'completed' else None
        folder_id = folder_tc[idx % len(folder_tc)] if folder_tc else None
        suite_name = suite_id_to_name.get(suite_id, f'用例集{suite_id}')
        tasks_data.append((
            f'【用例】{mod_name}-{suite_name}', f'WPS邮箱 {mod_name} 用例执行', folder_id, 'test_case', 'high' if idx < 3 else 'medium',
            status, uid_creator, executor_id, project_id, iteration_ids[idx % len(iteration_ids)], suite_id, req_id,
            scheduled_start, scheduled_end, started_time, completed_time,
            None, None, None, None,
        ))
    cursor.executemany("""
        INSERT INTO test_tasks (task_name, task_description, folder_id, task_type, priority, status, creator_id, executor_id, project_id, iteration_id, suite_id, version_requirement_id, scheduled_time, scheduled_end_time, started_time, completed_time, script_file, file_path, file_hash, command)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, tasks_data)
    cursor.execute("SELECT id, suite_id, status, project_id, iteration_id FROM test_tasks WHERE task_type = 'test_case' ORDER BY id")
    task_rows = cursor.fetchall()

    for task_id, suite_id, _status, _proj_id, _iter_id in task_rows:
        for case_id in case_suite_map.get(suite_id, []):
            cursor.execute("INSERT INTO task_case_relation (task_id, case_id) VALUES (%s, %s)", (task_id, case_id))

    cursor.execute("SELECT id, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result FROM test_cases")
    case_rows = {row[0]: row for row in cursor.fetchall()}
    for task_id, suite_id, status, tproj_id, titer_id in task_rows:
        if status not in ('completed', 'running'):
            continue
        for case_id in case_suite_map.get(suite_id, []):
            row = case_rows.get(case_id)
            if not row:
                continue
            _, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result = row
            cursor.execute("""
                INSERT INTO task_case_snapshots (task_id, case_id, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (task_id, case_id, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result))

    exec_statuses = ['pass', 'fail', 'blocked', 'not_applicable']
    for ti, (task_id, suite_id, status, tproj_id, titer_id) in enumerate(task_rows):
        if status != 'completed':
            continue
        case_ids = case_suite_map.get(suite_id, [])
        for i, case_id in enumerate(case_ids):
            st_idx = (ti * 7 + i) % 10
            st = exec_statuses[0] if st_idx < 6 else (exec_statuses[1] if st_idx < 8 else (exec_statuses[2] if st_idx < 9 else exec_statuses[3]))
            cursor.execute("""
                INSERT INTO test_case_executions (task_id, case_id, project_id, iteration_id, status, executor_id, execution_time, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (task_id, case_id, tproj_id or project_id, titer_id or iteration_ids[0], st, uid_tester1, (now - timedelta(minutes=45)).strftime(time_fmt), '执行备注'))
    cursor.execute("""
        UPDATE test_cases tc
        INNER JOIN (SELECT case_id, status FROM test_case_executions e1 WHERE id = (SELECT MAX(id) FROM test_case_executions e2 WHERE e2.case_id = e1.case_id)) latest ON latest.case_id = tc.id
        SET tc.status = latest.status
    """)

    print("插入设备...")
    devices_data = [
        ('华为 P40', 'P40', 'android', '10', 'emulator-5554', 'offline', uid_owner),
        ('小米 11', 'MI 11', 'android', '11', 'emulator-5556', 'offline', uid_tester1),
        ('OPPO Find X3', 'PEDM00', 'android', '12', 'emulator-5558', 'offline', uid_tester2),
        ('vivo X60', 'V2055A', 'android', '11', 'emulator-5560', 'offline', uid_owner),
        ('Pixel 5 模拟器', 'Pixel 5', 'android', '13', 'emulator-5570', 'offline', uid_tester1),
    ]
    cursor.executemany("""
        INSERT INTO devices (device_name, device_model, os_type, os_version, device_id, status, owner_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, devices_data)
    cursor.execute("SELECT id FROM devices ORDER BY id")
    device_ids = [row[0] for row in cursor.fetchall()]

    print("插入设备脚本任务...")
    script_src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'get_device_info.py')
    backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
    storage_base = os.path.join(backend_dir, 'storage', 'device_scripts')
    date_str = now.strftime('%Y%m%d')
    script_date_dir = os.path.join(storage_base, date_str)
    os.makedirs(script_date_dir, exist_ok=True)
    unique_name = f"get_device_info_{uuid.uuid4().hex[:8]}.py"
    dest_path = os.path.join(script_date_dir, unique_name)
    if os.path.exists(script_src):
        shutil.copy2(script_src, dest_path)
    else:
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write('# WPS邮箱-设备信息采集脚本占位\nprint("get_device_info")\n')
    relative_path = f"{date_str}/{unique_name}"
    with open(dest_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    command = f"python {relative_path} --device-id $DEVICE_ID --adb-path adb"
    for i in range(3):
        scheduled_start = (now + timedelta(days=i)).strftime(time_fmt)
        scheduled_end = (now + timedelta(days=i, hours=2)).strftime(time_fmt)
        folder_id = folder_ds[i % len(folder_ds)] if folder_ds else None
        cursor.execute("""
            INSERT INTO test_tasks (task_name, task_description, folder_id, task_type, priority, status, creator_id, executor_id, project_id, iteration_id, suite_id, version_requirement_id, scheduled_time, scheduled_end_time, script_file, file_path, file_hash, command)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f'获取设备信息任务_{i+1}', '使用 get_device_info 脚本采集 Android 设备信息', folder_id, 'device_script', 'medium', 'pending',
            uid_creator, None, project_id, None, None, None, scheduled_start, scheduled_end,
            'get_device_info.py', relative_path, file_hash, command,
        ))
        script_task_id = cursor.lastrowid
        if device_ids:
            cursor.execute("INSERT INTO task_device_relation (task_id, device_id) VALUES (%s, %s)", (script_task_id, device_ids[i % len(device_ids)]))

    print("插入任务报告...")
    cursor.execute("""
        SELECT t.id, t.task_name, t.task_type, t.project_id, t.completed_time, t.suite_id, t.iteration_id, t.version_requirement_id
        FROM test_tasks t WHERE t.task_type = 'test_case' AND t.status = 'completed' ORDER BY t.id
    """)
    for row in cursor.fetchall():
        task_id, task_name, task_type, proj_id, completed_at, suite_id, iter_id, req_id = row
        cursor.execute("SELECT status, COUNT(*) FROM test_case_executions WHERE task_id = %s GROUP BY status", (task_id,))
        counts = {'pass': 0, 'fail': 0, 'blocked': 0, 'not_applicable': 0}
        for st, cnt in cursor.fetchall():
            if st in counts:
                counts[st] = cnt
        total_cases = sum(counts.values())
        pass_rate = round(counts['pass'] / total_cases * 100, 1) if total_cases else 0
        summary = {
            'total_cases': total_cases, 'executed_cases': total_cases,
            'pass_count': counts['pass'], 'fail_count': counts['fail'],
            'blocked_count': counts['blocked'], 'not_applicable_count': counts['not_applicable'],
            'pass_rate': pass_rate, 'suite_name': suite_id_to_name.get(suite_id, ''),
        }
        cursor.execute("SELECT suite_name FROM test_suites WHERE id = %s", (suite_id,))
        suite_name_row = cursor.fetchone()
        suite_name_snap = suite_name_row[0] if suite_name_row else ''
        req_name = ''
        if req_id:
            cursor.execute("SELECT requirement_name FROM version_requirements WHERE id = %s", (req_id,))
            rn = cursor.fetchone()
            req_name = rn[0] if rn else ''
        details = []
        cursor.execute("SELECT case_id, status FROM test_case_executions WHERE task_id = %s", (task_id,))
        for cid, st in cursor.fetchall():
            cursor.execute("SELECT case_number, case_name FROM test_cases WHERE id = %s", (cid,))
            cn_row = cursor.fetchone()
            details.append({'case_id': cid, 'case_number': cn_row[0] if cn_row else '', 'case_name': cn_row[1] if cn_row else '', 'status': st})
        cursor.execute("""
            INSERT INTO reports (task_id, report_type, task_name, project_id, project_name, summary, details, completed_at, creator_id, assignee_id, status, iteration_name, suite_id, suite_name, requirement_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            task_id, task_type, task_name, proj_id, 'WPS邮箱业务', json.dumps(summary), json.dumps(details), completed_at, uid_creator, uid_tester1,
            'completed', None, suite_id, suite_name_snap, req_name,
        ))
    print("WPS 邮箱业务数据插入完成。")
    return True


def insert_wps_meeting_business_data(connection):
    """
    插入 WPS 会议业务模拟数据（依赖现有 users 数据）。
    包含：单项目、迭代、需求、用例库、用例、标签/标记、任务、执行记录、报告。
    """
    cursor = connection.cursor()
    now = datetime.now()
    time_fmt = '%Y-%m-%d %H:%M:%S'

    cursor.execute("SELECT id FROM users ORDER BY id")
    user_ids = [row[0] for row in cursor.fetchall()]
    if not user_ids:
        print("错误：未找到任何用户，请先插入用户数据。")
        return False
    uid_owner = user_ids[0]
    uid_creator = user_ids[0]
    uid_tester1 = user_ids[1] if len(user_ids) > 1 else user_ids[0]
    uid_reviewer = user_ids[2] if len(user_ids) > 2 else user_ids[1]

    print("插入项目（WPS 会议）...")
    proj_start = (now - timedelta(days=90)).strftime(time_fmt)
    proj_end = (now + timedelta(days=60)).strftime(time_fmt)
    cursor.execute("""
        INSERT INTO projects (project_name, description, status, owner_id, creator_id, start_date, end_date, tags, priority, doc_url, pipeline_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        'WPS会议',
        'WPS 会议客户端相关功能测试：预约会议、入会、会中控制、录制、会管会控等。',
        'in_progress', uid_owner, uid_creator, proj_start, proj_end,
        json.dumps(['WPS', '会议', '移动端']), 'high',
        'https://docs.example.com/wps-meeting', 'https://pipeline.example.com/wps-meeting',
    ))
    project_id = cursor.lastrowid
    for i, uid in enumerate(user_ids[:5]):
        role = 'owner' if uid == uid_owner else ('manager' if i == 1 else 'tester')
        cursor.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s, %s, %s)", (project_id, uid, role))

    print("插入迭代（WPS 会议）...")
    iter_rows = [
        ('V1.0.0', '预约与入会', 'completed', -90, -55),
        ('V1.1.0', '会中控制与录制', 'completed', -50, -25),
        ('V2.0.0', '会管会控与体验', 'active', -20, 30),
    ]
    iteration_ids = []
    for name, goal, status, start_delta, end_delta in iter_rows:
        start_d = (now + timedelta(days=start_delta)).strftime(time_fmt)
        end_d = (now + timedelta(days=end_delta)).strftime(time_fmt)
        cursor.execute("""
            INSERT INTO iterations (project_id, iteration_name, description, goal, status, start_date, end_date, version, created_by, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (project_id, name, f'WPS会议 {name} 迭代', goal, status, start_d, end_d, name, uid_creator, uid_creator))
        iteration_ids.append(cursor.lastrowid)

    print("插入需求（WPS 会议）...")
    req_rows = [
        ('预约会议', '创建会议、日历邀请、重复会议、提醒', iteration_ids[0], 'completed'),
        ('入会与音视频', '入会方式、麦克风/摄像头、扬声器、美颜', iteration_ids[0], 'completed'),
        ('会中控制', '静音、共享屏幕、聊天、举手、签到', iteration_ids[1], 'completed'),
        ('录制与回放', '本地录制、云录制、回放', iteration_ids[1], 'completed'),
        ('会管会控', '主持人权限、踢人、锁定会议、等候室', iteration_ids[2], 'in_progress'),
    ]
    requirement_ids = []
    for idx, (mod_name, desc, iter_id, status) in enumerate(req_rows):
        priority = ['P0', 'P1', 'P2', 'P3'][idx % 4]
        cursor.execute("""
            INSERT INTO version_requirements (requirement_name, requirement_description, module, status, project_id, iteration_id, priority, estimated_hours, actual_hours, created_by, assigned_to, start_date, end_date, environment, is_deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f'需求-{mod_name}', desc, mod_name, status, project_id, iter_id, priority,
            8.0, 6.0, uid_creator, uid_tester1,
            (now - timedelta(days=60)).strftime(time_fmt), (now + timedelta(days=20)).strftime(time_fmt),
            'test', False,
        ))
        requirement_ids.append(cursor.lastrowid)

    print("插入用例库（WPS 会议功能模块 - 多层目录 + 多用例集）...")

    def _mk_folder_m(name, desc, parent_id, sort=0):
        cursor.execute("""
            INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
            VALUES (%s, %s, %s, 'folder', %s, %s, NULL, NULL, %s)
        """, (name, desc, parent_id, uid_creator, project_id, sort))
        return cursor.lastrowid

    def _mk_suite_m(name, desc, parent_id, req_id, iter_id, sort=0):
        cursor.execute("""
            INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
            VALUES (%s, %s, %s, 'suite', %s, %s, %s, %s, %s)
        """, (name, desc, parent_id, uid_creator, project_id, req_id, iter_id, sort))
        return cursor.lastrowid

    root_folder_id = _mk_folder_m('WPS会议用例库', '按会议功能划分', None)

    # 二级分类
    f_before = _mk_folder_m('会前', '预约与入会', root_folder_id, 0)
    f_during = _mk_folder_m('会中', '会中控制、录制', root_folder_id, 1)
    f_admin = _mk_folder_m('会管', '主持人权限管理', root_folder_id, 2)

    # 三级目录
    f_reserve = _mk_folder_m('预约会议', '预约相关场景', f_before, 0)
    f_join = _mk_folder_m('入会与音视频', '入会方式和音视频', f_before, 1)
    f_control = _mk_folder_m('会中控制与录制', '共享、聊天、录制', f_during, 0)

    MODULES = [
        ('预约会议', requirement_ids[0], 12),
        ('入会与音视频', requirement_ids[1], 15),
        ('会中控制与录制', requirement_ids[2], 18),
        ('会管会控', requirement_ids[4], 10),
    ]
    m_folder_map = {
        '预约会议': f_reserve, '入会与音视频': f_join,
        '会中控制与录制': f_control, '会管会控': f_admin,
    }

    # 部分目录下多个用例集
    m_extra = {
        '入会与音视频': ['入会方式用例集', '音视频控制用例集'],
        '会中控制与录制': ['共享与聊天用例集', '录制与回放用例集'],
    }

    suite_rows = []
    for idx, (mod_name, req_id, case_count) in enumerate(MODULES):
        parent_fid = m_folder_map.get(mod_name, root_folder_id)
        iter_id = iteration_ids[idx % len(iteration_ids)]
        if mod_name in m_extra:
            names = m_extra[mod_name]
            per = max(1, case_count // len(names))
            for si, sname in enumerate(names):
                sid = _mk_suite_m(sname, f'{mod_name} - {sname}', parent_fid, req_id, iter_id, si)
                suite_rows.append((sid, project_id, req_id, mod_name, per if si < len(names) - 1 else case_count - per * (len(names) - 1)))
        else:
            sid = _mk_suite_m(f'{mod_name}用例集', f'{mod_name} 相关用例', parent_fid, req_id, iter_id, 0)
            suite_rows.append((sid, project_id, req_id, mod_name, case_count))

    # 会议场景用例数据：(模块名 -> [(用例名, 测试数据, 前置条件, 步骤, 预期结果, 优先级)])
    WPS_MEETING_CASES = {
        '预约会议': [
            ('创建即时会议', None, '已登录WPS会议', '点击「快速会议」', '进入会议房间，可看到本地画面', 'P0'),
            ('创建预约会议', '会议主题：周会', '已登录', '点击「预约会议」，填写主题、时间、参与人', '预约成功，日历中显示', 'P0'),
            ('重复会议-每天', '重复：每天 10:00', '已登录', '预约会议时设置重复为每天', '生成系列会议', 'P1'),
            ('会议提醒', None, '已预约会议', '到达提醒时间', '收到提醒通知', 'P0'),
            ('修改预约会议', None, '已有预约会议', '编辑会议，修改时间', '会议信息更新成功', 'P1'),
            ('取消预约会议', None, '已有预约会议', '点击取消会议', '会议从列表移除', 'P1'),
        ],
        '入会与音视频': [
            ('入会-麦克风开启', None, '已收到会议邀请', '点击入会，保持麦克风开', '进入会议，他人可听到声音', 'P0'),
            ('入会-摄像头开启', None, '已收到邀请', '入会时开启摄像头', '他人可见画面', 'P0'),
            ('入会-仅听会', None, '已收到邀请', '入会时关闭麦克风和摄像头', '以听众身份进入', 'P0'),
            ('会中静音/取消静音', None, '已在会中', '点击静音按钮', '本地静音，他人听不到', 'P0'),
            ('会中关闭/开启摄像头', None, '已在会中', '关闭摄像头', '他人看到黑屏或头像', 'P0'),
            ('切换扬声器与听筒', None, '已在会中', '切换音频输出为听筒', '声音从听筒播放', 'P1'),
            ('美颜开关', None, '已开启摄像头', '开启美颜', '画面美颜效果生效', 'P2'),
        ],
        '会中控制与录制': [
            ('共享屏幕', None, '已在会中', '点击共享屏幕，选择应用/桌面', '与会者看到共享内容', 'P0'),
            ('停止共享', None, '正在共享屏幕', '点击停止共享', '共享结束', 'P0'),
            ('会中聊天', '发送文字：大家好', '已在会中', '打开聊天，输入文字发送', '所有人可见该消息', 'P0'),
            ('举手功能', None, '已在会中', '点击举手', '主持人看到举手状态', 'P1'),
            ('签到', None, '主持人已发起签到', '点击签到', '签到成功', 'P1'),
            ('开始云录制', None, '主持人', '点击录制-云录制', '录制开始，与会者看到录制提示', 'P0'),
            ('停止录制', None, '正在录制', '点击停止录制', '录制结束，可查看回放', 'P0'),
        ],
        '会管会控': [
            ('主持人移交', None, '主持人在会中', '将主持人移交给他人', '对方成为新主持人', 'P0'),
            ('踢出参会者', None, '主持人', '选择参会者-移出会议', '该成员被移出', 'P0'),
            ('锁定会议', None, '主持人', '开启锁定会议', '新成员无法加入', 'P1'),
            ('等候室', None, '主持人', '开启等候室', '新成员进入等候室，主持人可准入', 'P0'),
            ('全体静音', None, '主持人', '点击全体静音', '除主持人外全部静音', 'P1'),
        ],
    }
    cases_data = []
    case_seq = 0
    cases_by_suite = {}
    for suite_id, proj_id, req_id, mod_name, _n in suite_rows:
        module_cases = WPS_MEETING_CASES.get(mod_name, [])
        if not module_cases:
            continue
        suite_cases = []
        for c in module_cases:
            cname, td, pre, step, er, pri = c
            case_seq += 1
            case_number = f"TC-WPSM-{case_seq:04d}"
            suite_cases.append((case_number, cname, td, pre, step, er, pri))
            cases_data.append((
                case_number, cname, f'{mod_name} - {cname}', pri, uid_tester1,
                proj_id, req_id, iteration_ids[0], suite_id,
                pre, step, er, None, td,
                uid_tester1, uid_reviewer,
            ))
        cases_by_suite[suite_id] = suite_cases

    cursor.executemany("""
        INSERT INTO test_cases (case_number, case_name, case_description, priority, creator_id,
            project_id, version_requirement_id, iteration_id, suite_id,
            preconditions, steps, expected_result, actual_result, test_data,
            assignee_id, reviewer_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, cases_data)
    print(f"  共插入 {len(cases_data)} 条用例（WPS会议）")

    cursor.execute("SELECT id, suite_id, case_number FROM test_cases WHERE project_id = %s ORDER BY id", (project_id,))
    case_suite_map = {}
    case_id_by_number = {}
    for cid, sid, cnum in cursor.fetchall():
        case_suite_map.setdefault(sid, []).append(cid)
        case_id_by_number[cnum] = cid

    # 脑图数据与用例集统计
    print("生成脑图数据并回写（WPS会议）...")
    for suite_id, proj_id, req_id, mod_name, _n in suite_rows:
        module_cases = WPS_MEETING_CASES.get(mod_name, [])
        suite_case_tuples = cases_by_suite.get(suite_id, [])
        if not module_cases:
            continue
        root_children = []
        for idx, c in enumerate(module_cases):
            cname, td, pre, step, er, pri = c
            case_number = suite_case_tuples[idx][0] if idx < len(suite_case_tuples) else f'TC-WPSM-{idx+1:04d}'
            node_id = f'c-m-{suite_id}-{idx}'
            db_id = case_id_by_number.get(case_number)
            if db_id:
                cursor.execute("UPDATE test_cases SET mindmap_node_id=%s, group_path=%s WHERE id=%s", (node_id, mod_name, db_id))
            chain = [{'id': f'pc-m-{suite_id}-{idx}', 'text': pre, 'attribute': 'precondition',
                'children': [{'id': f'st-m-{suite_id}-{idx}', 'text': step, 'attribute': 'step',
                    'children': [{'id': f'er-m-{suite_id}-{idx}', 'text': er, 'attribute': 'expected_result'}]}]}]
            if td:
                chain = [{'id': f'td-m-{suite_id}-{idx}', 'text': td, 'attribute': 'test_data', 'children': chain}]
            root_children.append({'id': node_id, 'text': cname, 'attribute': 'case_title', 'priority': pri, 'children': chain})
        total = len(module_cases)
        mindmap_json = json.dumps({
            'version': '2.0',
            'root': {'id': 'root', 'text': f'{mod_name}用例集', 'children': root_children},
            'metadata': {'total_cases': total, 'last_saved_at': now.strftime(time_fmt), 'last_saved_by': uid_creator},
        }, ensure_ascii=False)
        cursor.execute(
            "UPDATE test_suites SET case_mindmap_data=%s, case_count=%s, review_status=%s, case_edit_status=%s, last_saved_at=%s, last_saved_by=%s WHERE id=%s",
            (mindmap_json, total, 'not_reviewed', 'drafting', now.strftime(time_fmt), uid_creator, suite_id))

    print("插入标签和标记（WPS会议）...")
    tag_data = [
        ('会议核心', '#67C23A', project_id, uid_creator),
        ('音视频', '#E6A23C', project_id, uid_creator),
        ('会管会控', '#409EFF', project_id, uid_creator),
    ]
    cursor.executemany(
        "INSERT INTO case_tags (tag_name, tag_color, project_id, creator_id) VALUES (%s,%s,%s,%s)",
        tag_data)
    marker_names_meeting = ['会议专项', '兼容性', '性能']
    for i, name in enumerate(marker_names_meeting):
        cursor.execute(
            "INSERT INTO case_markers (marker_name, marker_type, project_id, creator_id) VALUES (%s,%s,%s,%s)",
            (name, 'custom', project_id, uid_creator))

    # 任务文件夹为全局，不再重复创建；直接使用已有 test_case 文件夹
    cursor.execute("SELECT id FROM task_folders WHERE task_type = 'test_case' ORDER BY sort_order LIMIT 1")
    folder_row = cursor.fetchone()
    folder_id = folder_row[0] if folder_row else None

    print("插入测试任务（WPS会议）...")
    suite_id_to_name = {r[0]: r[3] for r in suite_rows}
    for idx, row in enumerate(suite_rows[:2]):  # 只插入前 2 个用例集的任务
        suite_id, proj_id, req_id, mod_name, _ = row
        status = 'completed' if idx == 0 else 'pending'
        executor_id = uid_tester1 if status == 'completed' else None
        scheduled_start = (now - timedelta(days=2)).strftime(time_fmt)
        scheduled_end = (now + timedelta(days=1)).strftime(time_fmt)
        started_time = (now - timedelta(hours=1)).strftime(time_fmt) if status == 'completed' else None
        completed_time = (now - timedelta(minutes=20)).strftime(time_fmt) if status == 'completed' else None
        suite_name = suite_id_to_name.get(suite_id, f'用例集{suite_id}')
        cursor.execute("""
            INSERT INTO test_tasks (task_name, task_description, folder_id, task_type, priority, status, creator_id, executor_id, project_id, iteration_id, suite_id, version_requirement_id, scheduled_time, scheduled_end_time, started_time, completed_time, script_file, file_path, file_hash, command)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f'【用例】WPS会议-{mod_name}', f'WPS会议 {mod_name} 用例执行', folder_id, 'test_case', 'high',
            status, uid_creator, executor_id, project_id, iteration_ids[idx % len(iteration_ids)], suite_id, req_id,
            scheduled_start, scheduled_end, started_time, completed_time,
            None, None, None, None,
        ))
        task_id = cursor.lastrowid
        for case_id in case_suite_map.get(suite_id, []):
            cursor.execute("INSERT INTO task_case_relation (task_id, case_id) VALUES (%s, %s)", (task_id, case_id))
        if status == 'completed':
            cursor.execute("SELECT id, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result FROM test_cases WHERE suite_id = %s", (suite_id,))
            for row in cursor.fetchall():
                cid, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result = row
                cursor.execute("""
                    INSERT INTO task_case_snapshots (task_id, case_id, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (task_id, cid, case_number, case_name, priority, test_data, preconditions, steps, expected_result, actual_result))
            for case_id in case_suite_map.get(suite_id, []):
                st = 'pass' if (case_id % 3 != 0) else 'fail'
                cursor.execute("""
                    INSERT INTO test_case_executions (task_id, case_id, project_id, iteration_id, status, executor_id, execution_time, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (task_id, case_id, proj_id, iteration_ids[0], st, uid_tester1, (now - timedelta(minutes=15)).strftime(time_fmt), '执行备注'))

    # 报告（仅对已完成的会议任务）
    cursor.execute("""
        SELECT t.id, t.task_name, t.task_type, t.project_id, t.completed_time, t.suite_id, t.iteration_id, t.version_requirement_id
        FROM test_tasks t WHERE t.project_id = %s AND t.task_type = 'test_case' AND t.status = 'completed' ORDER BY t.id
    """, (project_id,))
    for row in cursor.fetchall():
        task_id, task_name, task_type, proj_id, completed_at, suite_id, iter_id, req_id = row
        cursor.execute("SELECT status, COUNT(*) FROM test_case_executions WHERE task_id = %s GROUP BY status", (task_id,))
        counts = {'pass': 0, 'fail': 0, 'blocked': 0, 'not_applicable': 0}
        for st, cnt in cursor.fetchall():
            if st in counts:
                counts[st] = cnt
        total_cases = sum(counts.values())
        pass_rate = round(counts['pass'] / total_cases * 100, 1) if total_cases else 0
        summary = {
            'total_cases': total_cases, 'executed_cases': total_cases,
            'pass_count': counts['pass'], 'fail_count': counts['fail'],
            'blocked_count': counts['blocked'], 'not_applicable_count': counts['not_applicable'],
            'pass_rate': pass_rate, 'suite_name': suite_id_to_name.get(suite_id, ''),
        }
        cursor.execute("SELECT suite_name FROM test_suites WHERE id = %s", (suite_id,))
        suite_name_row = cursor.fetchone()
        suite_name_snap = suite_name_row[0] if suite_name_row else ''
        req_name = ''
        if req_id:
            cursor.execute("SELECT requirement_name FROM version_requirements WHERE id = %s", (req_id,))
            rn = cursor.fetchone()
            req_name = rn[0] if rn else ''
        cursor.execute("SELECT case_id, status FROM test_case_executions WHERE task_id = %s", (task_id,))
        details = []
        for cid, st in cursor.fetchall():
            cursor.execute("SELECT case_number, case_name FROM test_cases WHERE id = %s", (cid,))
            cn_row = cursor.fetchone()
            details.append({'case_id': cid, 'case_number': cn_row[0] if cn_row else '', 'case_name': cn_row[1] if cn_row else '', 'status': st})
        cursor.execute("""
            INSERT INTO reports (task_id, report_type, task_name, project_id, project_name, summary, details, completed_at, creator_id, assignee_id, status, iteration_name, suite_id, suite_name, requirement_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            task_id, task_type, task_name, proj_id, 'WPS会议', json.dumps(summary), json.dumps(details), completed_at, uid_creator, uid_tester1,
            'completed', None, suite_id, suite_name_snap, req_name,
        ))

    print("WPS 会议业务数据插入完成。")
    return True


def insert_test_data():
    """插入测试数据：用户（不变）+ WPS 邮箱业务 + WPS 会议业务模拟数据。"""
    connection = get_db_connection()
    if not connection:
        return False

    try:
        with connection.cursor() as cursor:
            # 1. 清空现有数据
            print("开始清空现有数据...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            tables = [
                'reports', 'user_settings', 'system_settings',
                'version_requirements', 'test_cases', 'test_tasks',
                'task_folders',
                'iterations', 'project_members', 'projects',
                'devices', 'test_suites', 'test_case_review_details',
                'test_case_review_history', 'test_suite_review_history',
                'test_suite_review_tasks', 'task_case_snapshots',
                'task_case_relation', 'task_device_relation', 'test_case_executions',
                'case_tags', 'case_markers',
                'users'
            ]
            for table in tables:
                cursor.execute(f"TRUNCATE TABLE {table}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            print("现有数据清空完成！")

            # 2. 插入用户数据（与原有一致）
            print("开始插入用户数据...")
            password = "123321"
            password_hash = generate_password_hash(password)
            initial_users = [
                ('Lethe', '13800138000', '超级管理员', 'male', '管理部', password_hash, 'super'),
                ('Manager', '13800138001', '项目经理', 'male', '项目部', password_hash, 'manager'),
                ('Tester', '13800138002', '测试主管', 'female', '测试部', password_hash, 'tester'),
                ('Admin', '13800138003', '普通成员', 'female', '测试部', password_hash, 'admin')
            ]
            cursor.executemany("""
                INSERT INTO users (username, phone, real_name, gender, department, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, initial_users)
            users_data = [
                ('linyuming', '13800138004', '林裕铭', 'male', '测试部', password_hash, 'manager'),
                ('zhoujin', '13800138005', '周瑾', 'female', '测试部', password_hash, 'manager'),
                ('chenguohui', '13800138006', '陈国慧', 'male', '测试部', password_hash, 'manager'),
                ('linsen', '13800138007', '林森', 'male', '测试部', password_hash, 'manager'),
                ('zhangjunhao', '13800138008', '张俊浩', 'male', '测试部', password_hash, 'manager'),
                ('wanghaoran', '13800138009', '王灏然', 'male', '测试部', password_hash, 'manager'),
                ('cuhongli', '13800138010', '储宏丽', 'female', '测试部', password_hash, 'manager'),
            ]
            cursor.executemany("""
                INSERT INTO users (username, phone, real_name, gender, department, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, users_data)
            print("用户测试数据插入成功！")

        # 3. 插入 WPS 邮箱业务数据
        if not insert_wps_email_business_data(connection):
            return False
        # 4. 插入 WPS 会议业务数据
        if not insert_wps_meeting_business_data(connection):
            return False
        connection.commit()
        print("所有测试数据插入成功！")
        print("测试账号信息：")
        print("   - 特殊账号（保留）：Lethe(超级管理员), Manager(项目经理), Tester(测试主管), Admin(系统管理员)")
        print("   - 测试用户：林裕铭、周瑾、陈国慧、林森、张俊浩、王灏然、储宏丽")
        print("   - 用户名为姓名拼音，密码统一为：123321，角色均为 manager（管理员）")
        return True

    except Exception as e:
        print(f"插入测试数据失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def main():
    """主函数"""
    print("开始插入测试数据（用户 + WPS 邮箱业务 + WPS 会议业务）...")
    if insert_test_data():
        print("测试数据插入完成！")
        return 0
    print("测试数据插入失败！")
    return 1


if __name__ == "__main__":
    sys.exit(main())
