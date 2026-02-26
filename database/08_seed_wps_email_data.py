#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WPS 邮箱业务模拟数据脚本（重构版）

说明：
- 单一业务：WPS 邮箱
- 迭代：6 个（V1.0.0～V2.2.0），覆盖邮箱业务节奏
- 需求：16 条，覆盖写邮件、收件箱、发件箱、草稿、标签、搜索、账号、通知、专项等
- 用例库：根目录下多功能模块（写邮件与发信、附件与签名、收件箱、发件箱、草稿、定时与模板、标签与分类、账号与同步、通知与显示、搜索、过滤与规则、已读回执与撤回、多账号、专项），对应用例数量增多
- 用例评审：待我评审/我发起的评审/评审历史数据多，覆盖所有用户（每用户作为发起人、评审人均有较多记录），含 pending/in_review/completed/rejected
- 测试任务目录：覆盖邮箱功能模块；测试任务数量多，状态含 pending、running、completed
- 任务用例快照：对已完成/进行中任务写入 task_case_snapshots，便于报告与历史追溯
- 测试报告：每个已完成用例任务生成一条报告，summary 来自执行统计（通过率等）

运行方式（在项目根目录下）：
  python database/08_seed_wps_email_data.py

依赖：需先存在 users 表数据；数据库配置见 database/config.py
"""

import os
import sys
import json
import uuid
import hashlib
import shutil
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import DB_CONFIG

try:
    import pymysql
except ImportError:
    print("请安装 pymysql: pip install pymysql")
    sys.exit(1)


def get_db_connection():
    try:
        return pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG.get('charset', 'utf8mb4'),
        )
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


# 需清空的表（不包含 users、user_settings、system_settings）
TABLES_TO_TRUNCATE = [
    'reports',
    'test_case_review_history',
    'test_suite_review_history',
    'test_case_review_details',
    'test_suite_review_tasks',
    'task_case_snapshots',
    'task_device_relation',
    'task_case_relation',
    'test_case_executions',
    'test_tasks',
    'task_folders',
    'test_cases',
    'test_suites',
    'version_requirements',
    'iterations',
    'project_members',
    'projects',
    'devices',
]


def run(connection):
    cursor = connection.cursor()
    now = datetime.now()
    time_fmt = '%Y-%m-%d %H:%M:%S'

    # ---------- 1. 清空业务数据（保留用户与系统设置）----------
    print("清空业务表数据（保留 users / user_settings / system_settings）...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in TABLES_TO_TRUNCATE:
        cursor.execute(f"TRUNCATE TABLE `{table}`")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    connection.commit()
    print("清空完成。")

    # ---------- 2. 获取现有用户 ID ----------
    cursor.execute("SELECT id FROM users ORDER BY id")
    user_ids = [row[0] for row in cursor.fetchall()]
    if not user_ids:
        print("错误：未找到任何用户，请先保证 users 表中有数据。")
        return False
    uid_owner = user_ids[0]
    uid_creator = user_ids[0]
    uid_tester1 = user_ids[1] if len(user_ids) > 1 else user_ids[0]
    uid_tester2 = user_ids[2] if len(user_ids) > 2 else user_ids[0]
    uid_reviewer = user_ids[2] if len(user_ids) > 2 else user_ids[1]

    # ---------- 3. 项目：WPS 邮箱业务 ----------
    print("插入项目...")
    proj_start = (now - timedelta(days=120)).strftime(time_fmt)
    proj_end = (now + timedelta(days=90)).strftime(time_fmt)
    cursor.execute("""
        INSERT INTO projects (project_name, description, status, owner_id, creator_id, start_date, end_date, tags, priority, doc_url, pipeline_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        'WPS邮箱业务',
        'WPS 邮箱客户端相关功能与专项测试，包含写邮件、收件箱、设置、账号同步等模块。',
        'in_progress',
        uid_owner,
        uid_creator,
        proj_start,
        proj_end,
        json.dumps(['WPS', '邮箱', '移动端']),
        'high',
        'https://docs.example.com/wps-email',
        'https://pipeline.example.com/wps-email',
    ))
    project_id = cursor.lastrowid
    connection.commit()

    # 项目成员
    for i, uid in enumerate(user_ids[:6]):
        role = 'owner' if uid == uid_owner else ('manager' if i == 1 else 'tester')
        cursor.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s, %s, %s)", (project_id, uid, role))
    connection.commit()

    # ---------- 4. 迭代：VX.X.X（增多，覆盖邮箱业务节奏）----------
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
    connection.commit()

    # ---------- 5. 需求（增多，覆盖邮箱业务功能）----------
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
    req_priorities = ['high', 'medium', 'high', 'medium', 'low']
    for idx, (mod_name, desc, iter_id, status) in enumerate(req_rows):
        priority = req_priorities[idx % len(req_priorities)]
        cursor.execute("""
            INSERT INTO version_requirements (requirement_name, requirement_description, module, status, project_id, iteration_id, priority, estimated_hours, actual_hours, created_by, assigned_to, start_date, end_date, environment, is_deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f'需求-{mod_name}', desc, mod_name, status,
            project_id, iter_id, priority, 12.0 + (idx % 5) * 2, 10.0, uid_creator, uid_tester1,
            (now - timedelta(days=90)).strftime(time_fmt), (now + timedelta(days=30)).strftime(time_fmt),
            'test', False,
        ))
        requirement_ids.append(cursor.lastrowid)
    connection.commit()

    # ---------- 6. 用例库：按邮箱功能模块（根 + 多模块文件夹 + 用例集）----------
    print("插入用例库（邮箱功能模块目录）...")
    cursor.execute("""
        INSERT INTO test_suites (suite_name, description, parent_id, `type`, creator_id, project_id, version_requirement_id, iteration_id, sort_order)
        VALUES (%s, %s, NULL, 'folder', %s, %s, NULL, NULL, 0)
    """, ('WPS邮箱用例库', '按邮箱功能模块划分：写邮件、收件箱、发件箱、草稿、标签、搜索、账号、通知、专项等', uid_creator, project_id))
    root_folder_id = cursor.lastrowid

    # 邮箱功能模块（参考常见邮箱客户端）：文件夹 + 用例集，对应需求
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
    suite_rows = []  # (suite_id, project_id, req_id, module_name)
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
    connection.commit()

    # ---------- 7. 测试用例（按模块 case_count）----------
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
    connection.commit()

    # 用例 id 按 suite 归组
    cursor.execute("SELECT id, suite_id FROM test_cases")
    case_suite_map = {}
    for cid, sid in cursor.fetchall():
        case_suite_map.setdefault(sid, []).append(cid)

    # ---------- 8. 用例评审任务 + 评审详情 + 评审历史（覆盖所有用户，数据量多）----------
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
    connection.commit()

    # ---------- 9. 任务文件夹（覆盖邮箱功能模块）----------
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
    connection.commit()

    # ---------- 10. 测试任务（多种状态 + 用例快照 + 执行记录 + 报告）----------
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
    connection.commit()
    cursor.execute("SELECT id, suite_id, status, project_id, iteration_id FROM test_tasks WHERE task_type = 'test_case' ORDER BY id")
    task_rows = cursor.fetchall()

    # 任务-用例关联
    for task_id, suite_id, _status, _proj_id, _iter_id in task_rows:
        for case_id in case_suite_map.get(suite_id, []):
            cursor.execute("INSERT INTO task_case_relation (task_id, case_id) VALUES (%s, %s)", (task_id, case_id))
    connection.commit()

    # 用例快照（已完成/进行中任务写入快照，便于报告与历史追溯）
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
    connection.commit()

    # 用例执行记录（仅已完成任务，不同任务不同通过/失败分布）
    exec_statuses = ['pass', 'fail', 'blocked', 'not_applicable']
    for ti, (task_id, suite_id, status, tproj_id, titer_id) in enumerate(task_rows):
        if status != 'completed':
            continue
        case_ids = case_suite_map.get(suite_id, [])
        for i, case_id in enumerate(case_ids):
            # 不同任务不同比例：部分任务通过率高，部分低
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
    connection.commit()

    # ---------- 11. 设备（仅 Android）----------
    print("插入设备（仅 Android）...")
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
    connection.commit()

    # ---------- 12. 设备脚本任务（获取设备信息）----------
    print("插入设备脚本任务...")
    script_src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'get_device_info.py')
    backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
    storage_base = os.path.join(backend_dir, 'storage', 'device_scripts')
    date_str = now.strftime('%Y%m%d')
    script_date_dir = os.path.join(storage_base, date_str)
    os.makedirs(script_date_dir, exist_ok=True)
    script_filename = 'get_device_info.py'
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
            script_filename, relative_path, file_hash, command,
        ))
        script_task_id = cursor.lastrowid
        if device_ids:
            cursor.execute("INSERT INTO task_device_relation (task_id, device_id) VALUES (%s, %s)", (script_task_id, device_ids[i % len(device_ids)]))
    connection.commit()

    # ---------- 13. 任务报告（每个已完成用例任务一条，summary 来自执行统计）----------
    print("插入任务报告...")
    cursor.execute("""
        SELECT t.id, t.task_name, t.task_type, t.project_id, t.completed_time, t.suite_id, t.iteration_id, t.version_requirement_id
        FROM test_tasks t WHERE t.task_type = 'test_case' AND t.status = 'completed' ORDER BY t.id
    """)
    for row in cursor.fetchall():
        task_id, task_name, task_type, proj_id, completed_at, suite_id, iter_id, req_id = row
        cursor.execute("""
            SELECT status, COUNT(*) FROM test_case_executions WHERE task_id = %s GROUP BY status
        """, (task_id,))
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
    connection.commit()

    print("WPS 邮箱业务模拟数据插入完成。")
    return True


def main():
    print("=" * 60)
    print("WPS 邮箱业务模拟数据脚本")
    print("说明：不修改 users / user_settings / system_settings")
    print("=" * 60)
    conn = get_db_connection()
    if not conn:
        return 1
    try:
        if run(conn):
            return 0
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
