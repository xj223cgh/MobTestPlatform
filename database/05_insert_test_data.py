#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 插入测试数据

插入内容：用户（与原有一致）+ WPS 邮箱业务模拟数据（单项目、迭代、需求、用例库、任务、评审、设备、报告等）。
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
        'WPS邮箱业务',
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

    print("插入用例库（邮箱功能模块）...")
    cursor.execute("""
        INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
        VALUES (%s, %s, NULL, 'folder', %s, %s, NULL, NULL, 0)
    """, ('WPS邮箱用例库', '按邮箱功能模块划分：写邮件、收件箱、发件箱、草稿、标签、搜索、账号、通知、专项等', uid_creator, project_id))
    root_folder_id = cursor.lastrowid
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
    suite_rows = []
    for idx, (mod_name, req_id, case_count) in enumerate(MODULES):
        cursor.execute("""
            INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
            VALUES (%s, %s, %s, 'folder', %s, %s, NULL, NULL, %s)
        """, (mod_name, f'{mod_name} 功能模块', root_folder_id, uid_creator, project_id, idx))
        folder_id = cursor.lastrowid
        iter_id = iteration_ids[idx % len(iteration_ids)]
        cursor.execute("""
            INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
            VALUES (%s, %s, %s, 'suite', %s, %s, %s, %s, 0)
        """, (f'{mod_name}用例集', f'{mod_name} 相关用例', folder_id, uid_creator, project_id, req_id, iter_id))
        suite_rows.append((cursor.lastrowid, project_id, req_id, mod_name, case_count))

    print("插入测试用例...")
    CASE_TEMPLATES = [
        {'name': '正常流程', 'pre': '环境就绪', 'steps': '1. 打开功能\n2. 按步骤操作\n3. 提交', 'expected': '结果符合预期', 'data': None},
        {'name': '边界校验', 'pre': '已登录', 'steps': '1. 输入边界值\n2. 提交', 'expected': '校验通过或提示正确', 'data': '边界数据'},
        {'name': '异常处理', 'pre': '网络正常', 'steps': '1. 模拟异常\n2. 观察提示', 'expected': '有友好提示且不崩溃', 'data': None},
        {'name': '权限与状态', 'pre': '多账号', 'steps': '1. 切换账号/状态\n2. 操作功能', 'expected': '状态一致、权限正确', 'data': None},
        {'name': '兼容与性能', 'pre': '设备就绪', 'steps': '1. 执行场景\n2. 观察响应', 'expected': '无卡顿、数据正确', 'data': None},
    ]
    priorities = ['P0', 'P1', 'P2', 'P3']
    cases_data = []
    case_seq = 0
    for suite_id, proj_id, req_id, mod_name, n in suite_rows:
        iter_id = iteration_ids[0]
        for m in range(n):
            case_seq += 1
            tpl = CASE_TEMPLATES[m % len(CASE_TEMPLATES)]
            case_number = f"TC-WPS-{case_seq:04d}"
            case_name = f"{mod_name}-{tpl['name']}" + (f"({m // len(CASE_TEMPLATES) + 1})" if m >= len(CASE_TEMPLATES) else "")
            cases_data.append((
                case_number, case_name, f'{mod_name} 相关测试', priorities[m % 4], uid_tester1,
                proj_id, req_id, iter_id, suite_id,
                tpl['pre'], tpl['steps'], tpl['expected'], None, tpl['data'],
                uid_tester1, uid_reviewer,
            ))
    cursor.executemany("""
        INSERT INTO test_cases (case_number, case_name, case_description, priority, creator_id, project_id, version_requirement_id, iteration_id, suite_id, preconditions, steps, expected_result, actual_result, test_data, assignee_id, reviewer_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, cases_data)

    cursor.execute("SELECT id, suite_id FROM test_cases")
    case_suite_map = {}
    for cid, sid in cursor.fetchall():
        case_suite_map.setdefault(sid, []).append(cid)

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


def insert_test_data():
    """插入测试数据：用户（不变）+ WPS 邮箱业务模拟数据。"""
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
                ('zhaomin', '13800138004', '赵敏', 'female', '测试部', password_hash, 'tester'),
                ('chenjing', '13800138005', '陈静', 'female', '测试部', password_hash, 'tester'),
                ('yangfan', '13800138006', '杨帆', 'male', '开发部', password_hash, 'manager'),
                ('zhoujie', '13800138007', '周杰', 'male', '产品部', password_hash, 'admin'),
                ('wulei', '13800138008', '吴磊', 'male', '测试部', password_hash, 'tester'),
                ('zhengli', '13800138009', '郑丽', 'female', '测试部', password_hash, 'tester'),
                ('sunhao', '13800138010', '孙浩', 'male', '开发部', password_hash, 'manager')
            ]
            cursor.executemany("""
                INSERT INTO users (username, phone, real_name, gender, department, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, users_data)
            print("用户测试数据插入成功！")

        # 3. 插入 WPS 邮箱业务数据
        if not insert_wps_email_business_data(connection):
            return False
        connection.commit()
        print("所有测试数据插入成功！")
        print("测试账号信息：")
        print("   - 特殊账号（保留）：Lethe(超级管理员), Manager(项目经理), Tester(测试主管), Admin(系统管理员)")
        print("   - 测试用户：赵敏、陈静、杨帆、周杰、吴磊、郑丽、孙浩")
        print("   - 密码统一为：123321")
        return True

    except Exception as e:
        print(f"插入测试数据失败: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def main():
    """主函数"""
    print("开始插入测试数据（用户 + WPS 邮箱业务）...")
    if insert_test_data():
        print("测试数据插入完成！")
        return 0
    print("测试数据插入失败！")
    return 1


if __name__ == "__main__":
    sys.exit(main())
