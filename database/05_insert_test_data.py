#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本 - 插入测试数据

插入内容：用户 + 用例与项目管理业务 + 任务与设备管理业务（模拟数据）
（项目、迭代、需求、用例库、任务、评审、设备、报告等）。
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


# =====================================================================
# 项目1：用例与项目
# 覆盖：认证与账户、首页看板、项目管理、用例管理、用例评审、AI用例生成
# =====================================================================

def insert_case_and_project_data(connection):
    """插入 用例与项目 业务模拟数据。"""
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

    # ── 项目 ──
    print("插入项目（用例与项目管理）...")
    proj_start = (now - timedelta(days=120)).strftime(time_fmt)
    proj_end = (now + timedelta(days=90)).strftime(time_fmt)
    proj_created = (now - timedelta(days=120)).strftime(time_fmt)
    proj_updated = (now - timedelta(days=1)).strftime(time_fmt)
    cursor.execute("""
        INSERT INTO projects (project_name, description, status, owner_id, creator_id, start_date, end_date, tags, priority, doc_url, pipeline_url, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        '用例与项目管理',
        '认证、首页看板、项目管理、用例管理、用例评审、AI用例生成等核心功能。',
        'in_progress', uid_owner, uid_creator, proj_start, proj_end,
        json.dumps(['用例管理', 'Web平台']), 'high',
        'https://docs.example.com/mobtest-case', 'https://pipeline.example.com/mobtest-case',
        proj_created, proj_updated,
    ))
    project_id = cursor.lastrowid
    for i, uid in enumerate(user_ids[:6]):
        role = 'owner' if uid == uid_owner else ('manager' if i == 1 else 'tester')
        cursor.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s, %s, %s)", (project_id, uid, role))

    # ── 迭代 ──
    print("插入迭代...")
    iter_rows = [
        ('V1.0.0', '登录与项目基础', 'completed', -120, -80),
        ('V1.1.0', '用例管理与脑图', 'completed', -75, -45),
        ('V1.2.0', '用例评审与导入', 'completed', -40, -15),
        ('V2.0.0', 'AI用例生成与看板', 'active', -10, 25),
        ('V2.1.0', '批量操作与回收站', 'active', 5, 45),
        ('V2.2.0', '体验优化与专项', 'planning', 40, 75),
    ]
    iteration_ids = []
    for name, goal, status, start_delta, end_delta in iter_rows:
        start_d = (now + timedelta(days=start_delta)).strftime(time_fmt)
        end_d = (now + timedelta(days=end_delta)).strftime(time_fmt)
        cursor.execute("""
            INSERT INTO iterations (project_id, iteration_name, description, goal, status, start_date, end_date, version, created_by, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (project_id, name, f'用例与项目 {name} 迭代', goal, status, start_d, end_d, name, uid_creator, uid_creator))
        iteration_ids.append(cursor.lastrowid)

    # ── 需求 ──
    print("插入需求...")
    req_rows = [
        ('认证-登录登出', '会话登录、Cookie、登出清理', iteration_ids[0], 'completed'),
        ('认证-密码与个人中心', '忘记密码、邮箱验证码重置、个人信息修改', iteration_ids[0], 'completed'),
        ('首页看板', '平台统计、活动流、趋势图、设备状态', iteration_ids[0], 'completed'),
        ('项目CRUD与成员', '项目创建/编辑/删除、成员管理', iteration_ids[1], 'completed'),
        ('迭代与需求管理', '迭代CRUD、需求关联、覆盖率统计', iteration_ids[1], 'completed'),
        ('用例树与CRUD', '文件夹+用例集多级嵌套、用例增删改查', iteration_ids[1], 'completed'),
        ('脑图编辑器', '在线脑图编辑、版本管理、版本回滚', iteration_ids[2], 'completed'),
        ('用例评审', '发起评审、逐条审批、评审历史', iteration_ids[2], 'completed'),
        ('用例导入', 'Excel/第三方格式导入', iteration_ids[2], 'completed'),
        ('AI用例生成', '需求文档输入、异步生成、结果导入', iteration_ids[3], 'in_progress'),
        ('批量操作', '批量删除、移动、复制', iteration_ids[4], 'new'),
        ('回收站', '软删除与还原', iteration_ids[4], 'new'),
        ('标签与标记', '用例打标签与状态标记', iteration_ids[4], 'new'),
        ('脑图多人协作', '冲突检测与合并策略', iteration_ids[5], 'new'),
        ('专项-性能', '大量用例加载、脑图渲染性能', iteration_ids[5], 'new'),
        ('专项-权限', '角色权限边界校验', iteration_ids[5], 'new'),
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

    # ── 用例库（多级目录 + 用例集）──
    print("插入用例库（平台功能模块 - 多层目录 + 多用例集）...")

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

    root_folder_id = _mk_folder('用例与项目用例库', '按平台功能模块划分', None)

    f_auth = _mk_folder('认证与账户', '登录/登出/密码/个人中心', root_folder_id, 0)
    f_login = _mk_folder('登录与登出', '会话登录、Cookie、登出', f_auth, 0)
    f_password = _mk_folder('密码与个人中心', '忘记密码、个人信息', f_auth, 1)

    f_dashboard = _mk_folder('首页看板', '统计、活动流、趋势图', root_folder_id, 1)

    f_project = _mk_folder('项目管理', '项目CRUD、迭代、需求', root_folder_id, 2)
    f_proj_crud = _mk_folder('项目CRUD与成员', '创建/编辑/删除/成员', f_project, 0)
    f_iteration = _mk_folder('迭代与需求', '迭代管理、需求关联', f_project, 1)

    f_case = _mk_folder('用例管理', '用例树、CRUD、脑图', root_folder_id, 3)
    f_case_tree = _mk_folder('用例树与CRUD', '文件夹+用例集+用例', f_case, 0)
    f_mindmap = _mk_folder('脑图编辑器', '在线编辑、版本、回滚', f_case, 1)
    f_import = _mk_folder('导入与批量', '导入、批量操作、回收站', f_case, 2)

    f_review = _mk_folder('用例评审', '评审任务、单条审批、历史', root_folder_id, 4)
    f_ai = _mk_folder('AI用例生成', '异步生成、调试模式、知识库', root_folder_id, 5)
    f_special = _mk_folder('专项测试', '性能、权限', root_folder_id, 6)

    MODULES = [
        ('登录与登出', requirement_ids[0], 20),
        ('密码与个人中心', requirement_ids[1], 16),
        ('首页看板', requirement_ids[2], 18),
        ('项目CRUD与成员', requirement_ids[3], 22),
        ('迭代与需求管理', requirement_ids[4], 18),
        ('用例树与CRUD', requirement_ids[5], 28),
        ('脑图编辑器', requirement_ids[6], 25),
        ('用例评审', requirement_ids[7], 22),
        ('用例导入', requirement_ids[8], 14),
        ('AI用例生成', requirement_ids[9], 20),
        ('批量与回收站', requirement_ids[10], 16),
        ('标签与标记', requirement_ids[12], 12),
        ('专项-性能与权限', requirement_ids[14], 20),
    ]
    folder_map = {
        '登录与登出': f_login, '密码与个人中心': f_password,
        '首页看板': f_dashboard, '项目CRUD与成员': f_proj_crud,
        '迭代与需求管理': f_iteration, '用例树与CRUD': f_case_tree,
        '脑图编辑器': f_mindmap, '用例评审': f_review,
        '用例导入': f_import, 'AI用例生成': f_ai,
        '批量与回收站': f_import, '标签与标记': f_case_tree,
        '专项-性能与权限': f_special,
    }
    extra_suites_config = {
        '登录与登出': ['正常登录用例集', '异常登录用例集'],
        '用例树与CRUD': ['用例集结构用例集', '用例CRUD用例集', '用例排序与筛选用例集'],
        '脑图编辑器': ['脑图编辑用例集', '版本管理用例集'],
        'AI用例生成': ['生成任务用例集', '调试与知识库用例集'],
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

    # ── 用例数据 ──
    print("插入测试用例（MobTest平台场景）...")

    CASES = {
        '登录与登出': [
            ('正常登录', [
                ('使用正确用户名密码登录', '用户名: Tester, 密码: 123321', '用户已注册且状态正常', '输入用户名和密码，点击登录', '登录成功，跳转到首页看板', 'P0'),
                ('登录后Cookie会话有效', None, '已登录', '刷新页面', '保持登录状态，不跳转到登录页', 'P0'),
                ('登录成功后显示用户信息', None, '已登录', '查看页面右上角', '显示当前登录用户名和头像', 'P0'),
                ('正常登出', None, '已登录', '点击右上角头像，选择退出登录', '跳转到登录页，Cookie清除', 'P0'),
                ('登出后访问需鉴权页面', None, '已登出', '直接访问/test-cases页面', '重定向到登录页', 'P0'),
                ('记住登录状态', None, '用户已注册', '勾选"记住我"后登录', '关闭浏览器重新打开，保持登录状态', 'P1'),
            ]),
            ('异常登录', [
                ('密码错误登录', '用户名: Tester, 密码: wrong123', '用户已注册', '输入错误密码点击登录', '提示"用户名或密码错误"', 'P0'),
                ('用户名不存在', '用户名: notexist', '无此用户', '输入不存在的用户名', '提示"用户名或密码错误"', 'P0'),
                ('空用户名提交', '用户名为空', '登录页', '不填用户名直接点击登录', '提示"请输入用户名"', 'P1'),
                ('空密码提交', '密码为空', '登录页', '不填密码直接点击登录', '提示"请输入密码"', 'P1'),
                ('已停用用户登录', '用户状态: inactive', '用户已被管理员停用', '使用停用账号登录', '提示"账号已停用"', 'P1'),
                ('连续快速点击登录按钮', None, '已填写正确账号密码', '快速连续点击登录3次', '只触发一次登录请求', 'P1'),
                ('超长用户名/密码', '用户名: 500字符', '登录页', '输入超长字符串', '前端或后端截断，不报500错误', 'P2'),
            ]),
        ],
        '密码与个人中心': [
            ('忘记密码', [
                ('发送验证码到邮箱', '邮箱: test@example.com', '用户已绑定邮箱', '忘记密码页输入邮箱，点击发送验证码', '提示"验证码已发送"', 'P0'),
                ('使用正确验证码重置密码', '验证码: 正确6位', '已收到验证码', '输入验证码和新密码，提交', '密码重置成功，跳转登录页', 'P0'),
                ('错误验证码重置密码', '验证码: 000000', '已发送验证码', '输入错误验证码', '提示"验证码错误"', 'P0'),
                ('验证码过期', None, '验证码发送超过10分钟', '使用过期验证码', '提示"验证码已过期"', 'P1'),
                ('新密码与确认密码不一致', None, '已输入验证码', '新密码输入abc，确认密码输入xyz', '提示"两次密码不一致"', 'P1'),
                ('未绑定邮箱的用户', '用户无邮箱', '用户未绑定邮箱', '点击忘记密码', '提示"该账号未绑定邮箱"', 'P2'),
            ]),
            ('个人信息', [
                ('修改真实姓名', '新姓名: 张测试', '已登录，进入个人中心', '修改真实姓名并保存', '姓名更新成功', 'P0'),
                ('上传头像', '图片: avatar.jpg (200KB)', '已登录', '点击头像上传新图片', '头像更新，页面右上角同步显示', 'P1'),
                ('上传超大头像', '图片: 10MB', '已登录', '上传10MB图片', '提示"图片过大"', 'P2'),
                ('修改手机号', '新手机: 13900001111', '已登录', '修改手机号并保存', '手机号更新成功', 'P1'),
                ('手机号格式校验', '手机: abc123', '已登录', '输入非法手机号格式', '提示"手机号格式不正确"', 'P1'),
                ('修改密码', '旧密码正确，新密码: newpass123', '已登录', '输入旧密码和新密码，保存', '密码修改成功，需重新登录', 'P0'),
                ('旧密码错误时修改密码', '旧密码: wrongold', '已登录', '输入错误的旧密码', '提示"旧密码不正确"', 'P1'),
                ('修改部门信息', '部门: 质量部', '已登录', '修改部门并保存', '部门信息更新成功', 'P2'),
            ]),
        ],
        '首页看板': [
            ('统计概览', [
                ('平台统计数字正确', None, '数据库有项目/用例/设备/任务', '访问首页', '项目数、用例数、设备数、任务数与实际一致', 'P0'),
                ('活动流展示', None, '近期有操作记录', '查看活动流区域', '按时间倒序显示最近操作', 'P0'),
                ('趋势图渲染', None, '有历史数据', '查看趋势图', '折线图正常渲染，数据点正确', 'P1'),
                ('设备状态概览', None, '有设备数据', '查看设备状态区域', '在线/离线设备数准确', 'P1'),
                ('近期项目跳转', None, '有参与的项目', '点击某个近期项目', '跳转到该项目详情', 'P1'),
                ('无数据时看板兜底', None, '新用户，无任何数据', '访问首页', '各区域显示空状态提示，不报错', 'P2'),
                ('统计数字实时性', None, '已登录', '新建一个项目后刷新首页', '项目数+1', 'P1'),
            ]),
            ('看板交互', [
                ('切换统计时间范围', None, '看板有数据', '切换为"最近7天"', '趋势图数据刷新为7天范围', 'P1'),
                ('看板加载性能', None, '大量数据(100+项目)', '访问首页', '3秒内加载完成', 'P2'),
                ('不同角色看板权限', None, '只读用户登录', '查看看板', '只能看到有权项目的统计', 'P2'),
            ]),
        ],
        '项目CRUD与成员': [
            ('项目CRUD', [
                ('创建项目', '项目名: 测试项目A', '已登录，有创建权限', '点击新建项目，填写名称/描述/标签，提交', '项目创建成功，列表出现', 'P0'),
                ('创建项目-必填校验', None, '已登录', '不填项目名称直接提交', '提示"项目名称不能为空"', 'P0'),
                ('创建重名项目', '项目名: 已存在的项目名', '已有同名项目', '创建同名项目', '提示"项目名称已存在"', 'P1'),
                ('编辑项目信息', '修改描述', '已有项目', '编辑项目描述并保存', '项目信息更新成功', 'P0'),
                ('删除项目', None, '项目下无用例/任务', '点击删除项目', '项目从列表移除', 'P0'),
                ('删除有数据的项目', None, '项目下有用例/任务', '尝试删除', '弹出确认提示，确认后级联删除', 'P1'),
                ('项目列表搜索', '关键词: 测试', '有多个项目', '搜索框输入关键词', '列表过滤显示匹配项目', 'P1'),
                ('项目列表分页', None, '有20+个项目', '查看项目列表', '默认分页展示，切换页码正常', 'P2'),
            ]),
            ('成员管理', [
                ('添加项目成员', '用户: Tester', '已在项目中', '点击添加成员，选择用户', '成员添加成功', 'P0'),
                ('设置成员角色', None, '项目有成员', '修改成员角色为管理员', '角色更新成功', 'P0'),
                ('移除项目成员', None, '项目有非Owner成员', '点击移除成员', '成员从项目中移除', 'P1'),
                ('移除自己(Owner)', None, '当前用户是Owner', '尝试移除自己', '提示"不能移除项目拥有者"', 'P1'),
                ('非项目成员访问项目', None, '用户不在项目中', '通过URL直接访问项目', '返回403或提示无权限', 'P1'),
                ('成员列表展示', None, '项目有多个成员', '查看成员列表', '显示用户名、角色、加入时间', 'P2'),
            ]),
            ('需求管理', [
                ('创建版本需求', '需求名: 登录优化', '已有项目和迭代', '新建需求，填写名称/描述/关联迭代', '需求创建成功', 'P0'),
                ('需求关联迭代', None, '已有需求和迭代', '将需求关联到迭代', '迭代详情中显示该需求', 'P0'),
                ('编辑需求', None, '已有需求', '修改需求描述', '需求更新成功', 'P1'),
                ('删除需求', None, '已有需求', '删除需求', '需求从列表移除', 'P1'),
                ('需求状态变更', None, '需求状态为new', '将状态改为in_progress', '状态更新成功', 'P1'),
                ('需求覆盖率统计', None, '需求关联了用例', '查看迭代统计', '显示需求覆盖率百分比', 'P2'),
                ('需求筛选与排序', None, '有多条需求', '按优先级排序', '需求列表按优先级排列', 'P2'),
                ('无权限用户操作需求', None, '只读角色', '尝试创建需求', '提示无权限', 'P2'),
            ]),
        ],
        '迭代与需求管理': [
            ('迭代CRUD', [
                ('创建迭代', '迭代名: V3.0.0', '已有项目', '填写迭代名/目标/时间范围，提交', '迭代创建成功', 'P0'),
                ('创建迭代-必填校验', None, '已有项目', '不填名称提交', '提示"迭代名称不能为空"', 'P1'),
                ('编辑迭代', None, '已有迭代', '修改目标和结束日期', '迭代信息更新', 'P0'),
                ('删除迭代', None, '迭代下无需求/任务', '删除迭代', '迭代移除', 'P1'),
                ('删除有数据的迭代', None, '迭代下有需求', '尝试删除', '提示有关联数据，需确认', 'P1'),
                ('迭代状态流转', None, '迭代状态为planning', '修改为active', '状态更新成功', 'P1'),
                ('复制迭代', None, '已有迭代', '点击复制', '新迭代创建，信息复制但无用例数据', 'P2'),
            ]),
            ('迭代统计', [
                ('用例覆盖率', None, '迭代关联了需求和用例', '查看迭代详情', '显示覆盖率=有用例需求数/总需求数', 'P1'),
                ('执行进度', None, '迭代有关联任务', '查看迭代统计', '显示已执行/总用例数', 'P1'),
                ('迭代时间线', None, '有多个迭代', '查看时间线视图', '按时间排列显示各迭代', 'P2'),
                ('跨迭代数据隔离', None, '两个迭代有不同需求', '分别查看', '各迭代显示各自的需求和统计', 'P2'),
            ]),
        ],
        '用例树与CRUD': [
            ('用例集结构', [
                ('创建根文件夹', '文件夹名: 功能测试', '已有项目', '点击新建文件夹，输入名称', '文件夹出现在树中', 'P0'),
                ('创建子文件夹', '文件夹名: 登录模块', '已有根文件夹', '在根文件夹下创建子文件夹', '子文件夹嵌套显示', 'P0'),
                ('创建用例集', '名称: 正常登录用例集', '已有文件夹', '在文件夹下创建用例集', '用例集出现在文件夹下', 'P0'),
                ('重命名文件夹', None, '已有文件夹', '右键重命名', '文件夹名称更新', 'P1'),
                ('删除空文件夹', None, '文件夹为空', '删除文件夹', '删除成功', 'P1'),
                ('删除含子节点的文件夹', None, '文件夹下有用例集', '尝试删除', '提示有子节点，确认后级联删除', 'P1'),
                ('移动用例集到其他文件夹', None, '有两个文件夹', '拖拽移动用例集', '用例集出现在目标文件夹下', 'P1'),
                ('3级以上嵌套', None, '已有多级文件夹', '创建第4级文件夹', '正常嵌套显示', 'P2'),
                ('文件夹排序拖拽', None, '有多个同级文件夹', '拖拽调整排序', '排序更新', 'P2'),
            ]),
            ('用例CRUD', [
                ('新建用例', '用例名: 验证登录成功', '已有用例集', '打开用例集脑图，添加节点', '用例节点创建成功', 'P0'),
                ('编辑用例各字段', None, '已有用例', '修改用例名称/步骤/预期结果/优先级', '所有字段更新成功', 'P0'),
                ('设置用例优先级', '优先级: P0', '已有用例', '修改优先级为P0', '优先级更新，列表显示P0标签', 'P0'),
                ('删除用例', None, '已有用例', '在脑图中删除节点', '用例移入回收站', 'P0'),
                ('填写前置条件', None, '已有用例', '编辑前置条件字段', '前置条件保存成功', 'P1'),
                ('填写测试数据', None, '已有用例', '编辑测试数据字段', '测试数据保存成功', 'P1'),
                ('用例编号自动生成', None, '已有用例集', '新建用例', '自动生成唯一编号 TC-XXX-001', 'P1'),
                ('同名用例校验', '名称与已有用例重复', '用例集有同名用例', '创建同名用例', '允许创建（脑图模式不限制同名）或提示', 'P2'),
            ]),
            ('用例排序与筛选', [
                ('按优先级筛选', None, '用例集有P0-P3用例', '选择只看P0用例', '列表只显示P0用例', 'P1'),
                ('按状态筛选', None, '用例有不同执行状态', '筛选"已通过"用例', '只显示pass状态用例', 'P1'),
                ('用例搜索', '关键词: 登录', '用例集有用例', '搜索"登录"', '显示名称含"登录"的用例', 'P1'),
                ('搜索无结果', '关键词: zzzznotexist', '用例集有用例', '搜索不存在的关键词', '显示空结果提示', 'P2'),
                ('用例排序', None, '有多条用例', '按编号排序', '用例按编号升序排列', 'P2'),
            ]),
        ],
        '脑图编辑器': [
            ('脑图编辑', [
                ('打开用例集脑图', None, '用例集有用例', '点击脑图编辑', '脑图正常渲染，显示所有用例节点', 'P0'),
                ('添加用例节点', None, '已打开脑图', '选中分组节点，添加子节点', '新节点出现', 'P0'),
                ('编辑节点文本', None, '已有节点', '双击节点编辑文本', '文本更新成功', 'P0'),
                ('删除节点', None, '已有节点', '选中节点按Delete', '节点删除，子节点一并删除', 'P0'),
                ('拖拽移动节点', None, '已有多个节点', '拖拽节点到其他分组', '节点移动成功', 'P1'),
                ('展开/折叠子节点', None, '节点有子节点', '点击折叠按钮', '子节点隐藏/显示', 'P1'),
                ('脑图自动布局', None, '有20+节点', '点击自动布局', '节点重新排列，无重叠', 'P2'),
                ('脑图搜索', '关键词: 登录', '脑图有节点', '使用搜索功能', '匹配节点高亮', 'P1'),
                ('脑图全屏模式', None, '已打开脑图', '点击全屏按钮', '脑图全屏显示', 'P2'),
                ('空用例集打开脑图', None, '用例集无用例', '打开脑图', '显示空根节点，可开始添加', 'P1'),
            ]),
            ('版本管理', [
                ('自动保存版本', None, '已打开脑图并编辑', '编辑后等待自动保存', '版本快照生成', 'P0'),
                ('查看版本列表', None, '有多个版本', '点击版本历史', '显示版本列表和时间戳', 'P0'),
                ('版本回滚', None, '有多个版本', '选择历史版本，点击回滚', '脑图恢复到该版本状态', 'P0'),
                ('回滚后继续编辑', None, '已回滚到旧版本', '在旧版本基础上编辑', '正常编辑和保存', 'P1'),
                ('版本对比', None, '有两个版本', '选择两个版本对比', '高亮新增/删除/修改的节点', 'P2'),
            ]),
        ],
        '用例评审': [
            ('评审任务', [
                ('发起评审', None, '用例集有用例', '选择用例集，指定评审人，发起', '评审任务创建成功', 'P0'),
                ('发起评审-必填校验', None, '用例集有用例', '不选评审人直接提交', '提示"请选择评审人"', 'P1'),
                ('评审任务列表', None, '有评审任务', '查看评审中心', '按待处理/进行中/已完成分组显示', 'P0'),
                ('评审任务详情', None, '有进行中的评审', '点击评审任务', '显示用例列表和评审状态', 'P0'),
                ('逐条通过', None, '评审中有待审用例', '选择一条用例，点击通过', '该用例标记为已通过', 'P0'),
                ('逐条驳回并填评语', '评语: 步骤不清晰', '评审中有待审用例', '驳回并输入评语', '用例标记驳回，评语保存', 'P0'),
                ('批量通过', None, '有多条待审用例', '全选后批量通过', '所有用例标记通过', 'P1'),
                ('完成评审', None, '所有用例已审批', '点击完成评审', '评审状态变为completed', 'P0'),
            ]),
            ('评审历史与流程', [
                ('查看评审历史', None, '有已完成的评审', '查看历史记录', '显示历史评审列表和操作时间', 'P1'),
                ('驳回后重新发起', None, '评审已驳回', '修改用例后重新发起', '新评审任务创建', 'P1'),
                ('同一用例集多次评审', None, '用例集有历史评审', '再次发起评审', '新评审不影响历史记录', 'P2'),
                ('评审人收到通知', None, '发起评审', '检查评审人通知', '收到站内通知', 'P1'),
                ('非评审人无法审批', None, '用户不是评审人', '尝试操作通过/驳回', '提示无权限', 'P2'),
                ('评审统计', None, '有多条评审记录', '查看统计数据', '显示通过率、平均审批时间', 'P2'),
            ]),
        ],
        '用例导入': [
            ('导入功能', [
                ('Excel导入用例', '文件: cases.xlsx (标准模板)', '已有用例集', '上传Excel文件', '用例导入成功，数量正确', 'P0'),
                ('导入空Excel', '文件: empty.xlsx', '已有用例集', '上传空文件', '提示"文件无有效数据"', 'P1'),
                ('导入格式不匹配的Excel', '文件: 列名不正确', '已有用例集', '上传格式不匹配的文件', '提示列名映射错误', 'P1'),
                ('导入超大Excel', '文件: 5000行', '已有用例集', '上传5000行用例', '导入成功，耗时合理', 'P2'),
                ('导入重复用例', '文件含已存在的用例', '用例集有数据', '导入含重复行的文件', '提示重复行处理策略', 'P2'),
                ('导入含特殊字符', '用例名含emoji和特殊字符', '已有用例集', '导入含特殊字符的文件', '正常导入，字符不丢失', 'P2'),
            ]),
        ],
        'AI用例生成': [
            ('生成任务', [
                ('提交AI生成任务', '需求文档: 200字需求', '已有用例集', '输入需求文档，点击开始生成', '任务创建成功，显示生成中状态', 'P0'),
                ('生成任务状态轮询', None, '已创建生成任务', '页面自动轮询', '显示进度百分比', 'P0'),
                ('生成完成后用例入库', None, '生成任务已完成', '查看用例集', '新用例已写入，脑图有对应节点', 'P0'),
                ('空需求文档提交', '文档内容为空', '已有用例集', '不填文档直接提交', '提示"需求文档不能为空"', 'P1'),
                ('超长需求文档生成', '文档: 5000字', '已有用例集', '提交超长文档', '触发Map-Reduce分段生成', 'P1'),
                ('生成失败处理', None, 'AI接口返回异常', '等待任务完成', '任务状态变为failed，显示错误信息', 'P1'),
                ('生成过程中删除用例集', None, '生成任务进行中', '删除关联的用例集', '任务检测到用例集不存在，标记失败', 'P2'),
            ]),
            ('调试与知识库', [
                ('调试模式生成', None, '已有用例集', '开启调试模式开关后提交', '用例入库但不存入知识库', 'P0'),
                ('正常模式自动存入知识库', None, '已配置EMBEDDING_MODEL', '关闭调试模式提交', '用例入库且文档存入知识库', 'P1'),
                ('手动存入知识库', '文档内容: 100字', '已配置知识库', '调用store-to-kb接口', '文档成功存入知识库', 'P1'),
                ('知识库未配置时生成', None, 'EMBEDDING_MODEL未设置', '提交生成任务', '正常生成，跳过知识库检索', 'P1'),
                ('生成结果JSON解析失败重试', None, 'AI返回非标准JSON', '等待重试', '自动重试一次，成功则正常入库', 'P2'),
                ('用例字段校验修复', None, 'AI返回priority为"高"', '生成完成', '优先级自动映射为P0', 'P2'),
            ]),
        ],
        '批量与回收站': [
            ('批量操作', [
                ('批量删除用例', None, '用例集有多条用例', '勾选多条用例，点击批量删除', '所选用例移入回收站', 'P0'),
                ('批量移动用例', None, '有两个用例集', '勾选用例，移动到另一个用例集', '用例出现在目标用例集中', 'P1'),
                ('批量复制用例', None, '有两个用例集', '勾选用例，复制到另一个用例集', '目标用例集有副本，源用例集不变', 'P1'),
                ('全选再取消', None, '用例集有用例', '点击全选后再取消全选', '选中状态正确清除', 'P2'),
            ]),
            ('回收站', [
                ('查看回收站', None, '有已删除用例', '打开回收站', '显示被删除的用例列表', 'P0'),
                ('还原用例', None, '回收站有用例', '选中用例点击还原', '用例恢复到原用例集', 'P0'),
                ('永久删除', None, '回收站有用例', '选中后永久删除', '用例彻底清除', 'P1'),
                ('清空回收站', None, '回收站有多条记录', '点击清空', '回收站清空', 'P2'),
                ('已删除用例集下的用例还原', None, '用例集和用例都被删除', '还原用例', '提示原用例集不存在，需选择新目标', 'P2'),
            ]),
        ],
        '标签与标记': [
            ('标签管理', [
                ('创建标签', '标签名: 冒烟测试', '已有项目', '点击新建标签，选择颜色', '标签创建成功', 'P0'),
                ('给用例添加标签', None, '已有标签和用例', '在用例上添加标签', '用例显示标签标识', 'P0'),
                ('移除用例标签', None, '用例有标签', '移除标签', '标签从用例上消失', 'P1'),
                ('按标签筛选用例', None, '有标签的用例', '选择按某标签筛选', '只显示有该标签的用例', 'P1'),
                ('删除标签', None, '已有标签', '删除标签', '标签移除，已使用该标签的用例自动清理', 'P2'),
                ('重复标签名校验', '标签名已存在', '已有同名标签', '创建同名标签', '提示"标签名已存在"', 'P2'),
            ]),
            ('状态标记', [
                ('添加标记', None, '已有用例', '右键添加"待确认"标记', '用例显示标记', 'P1'),
                ('移除标记', None, '用例有标记', '移除标记', '标记消失', 'P1'),
                ('按标记筛选', None, '有标记的用例', '按标记筛选', '只显示有该标记的用例', 'P2'),
                ('自定义标记', '标记名: 需讨论', '已登录', '创建自定义标记', '标记创建成功', 'P2'),
            ]),
        ],
        '专项-性能与权限': [
            ('性能测试', [
            ]),
            ('权限边界', [
                ('只读用户不能创建项目', None, '只读角色登录', '尝试创建项目', '按钮不可用或提示无权限', 'P0'),
                ('只读用户不能编辑用例', None, '只读角色', '尝试编辑用例', '提示无权限', 'P0'),
                ('测试工程师可创建用例', None, '测试工程师角色', '创建用例', '创建成功', 'P0'),
                ('项目管理员可管理成员', None, '项目管理员角色', '添加/移除成员', '操作成功', 'P1'),
                ('越权访问他人项目API', None, '用户A不在项目B中', '直接调用项目B的API', '返回403', 'P1'),
                ('角色降级后权限立即生效', None, '管理员被降为只读', '降级后刷新页面', '不再能执行管理操作', 'P2'),
                ('超级管理员可访问所有', None, '超级管理员登录', '访问所有项目/操作', '全部可用', 'P1'),
                ('前端按钮与API双重校验', None, '前端禁用按钮但直接调API', '使用PostMan调用受限API', '后端也返回403', 'P1'),
            ]),
        ],
    }

    cases_data = []
    case_seq = 0
    cases_by_suite = {}
    for suite_id, proj_id, req_id, mod_name, _n in suite_rows:
        module_cases = CASES.get(mod_name, {})
        iter_id = iteration_ids[0]
        suite_cases = []
        for _group_name, group_cases in (module_cases if isinstance(module_cases, list) else module_cases.items()):
            group_list = group_cases if isinstance(group_cases, list) else _group_name
            if isinstance(_group_name, str) and isinstance(group_cases, list):
                for c in group_cases:
                    case_seq += 1
                    cname, td, pre, step, er, pri = c
                    case_number = f"TC-MTP-{case_seq:04d}"
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

    # ── 脑图 JSON ──
    print("生成脑图数据并回写...")
    for suite_id, proj_id, req_id, mod_name, _n in suite_rows:
        module_cases = CASES.get(mod_name, {})
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

    # ── 标签和标记 ──
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
    marker_names = ['未完成', '待确认', '待修改', '需讨论']
    marker_types = ['system', 'system', 'system', 'custom']
    for i, name in enumerate(marker_names):
        cursor.execute(
            "INSERT INTO case_markers (marker_name, marker_type, project_id, creator_id) VALUES (%s,%s,%s,%s)",
            (name, marker_types[i], project_id, uid_creator))

    # ── 评审 ──
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

    # ── 任务文件夹 ──
    print("插入任务文件夹...")
    folder_data = [
        ('认证与账户', None, 'test_case', 0),
        ('首页看板', None, 'test_case', 1),
        ('项目管理', None, 'test_case', 2),
        ('用例管理', None, 'test_case', 3),
        ('用例评审', None, 'test_case', 4),
        ('AI用例生成', None, 'test_case', 5),
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

    # ── 测试任务 ──
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
            f'【用例】{mod_name}-{suite_name}', f'用例与项目 {mod_name} 用例执行', folder_id, 'test_case', 'high' if idx < 3 else 'medium',
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

    # ── 设备 ──
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

    # ── 设备脚本任务 ──
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
            f.write('# MobTest-设备信息采集脚本占位\nprint("get_device_info")\n')
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

    # ── 报告 ──
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
            task_id, task_type, task_name, proj_id, '用例与项目', json.dumps(summary), json.dumps(details), completed_at, uid_creator, uid_tester1,
            'completed', None, suite_id, suite_name_snap, req_name,
        ))
    print("用例与项目 业务数据插入完成。")
    return True


# =====================================================================
# 项目2：任务与设备
# 覆盖：测试任务、测试报告、设备管理、系统管理、消息中心
# =====================================================================

def insert_task_and_device_data(connection):
    """插入 任务与设备 业务模拟数据。"""
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

    print("插入项目（任务与设备管理）...")
    proj_start = (now - timedelta(days=90)).strftime(time_fmt)
    proj_end = (now + timedelta(days=60)).strftime(time_fmt)
    proj_created = (now - timedelta(days=90)).strftime(time_fmt)
    proj_updated = now.strftime(time_fmt)
    cursor.execute("""
        INSERT INTO projects (project_name, description, status, owner_id, creator_id, start_date, end_date, tags, priority, doc_url, pipeline_url, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        '任务与设备管理',
        '测试任务管理、手工执行、设备脚本、报告、设备管理、系统管理、消息中心。',
        'in_progress', uid_owner, uid_creator, proj_start, proj_end,
        json.dumps(['任务管理', '设备管理']), 'high',
        'https://docs.example.com/mobtest-task', 'https://pipeline.example.com/mobtest-task',
        proj_created, proj_updated,
    ))
    project_id = cursor.lastrowid
    for i, uid in enumerate(user_ids[:5]):
        role = 'owner' if uid == uid_owner else ('manager' if i == 1 else 'tester')
        cursor.execute("INSERT INTO project_members (project_id, user_id, role) VALUES (%s, %s, %s)", (project_id, uid, role))

    print("插入迭代（任务与设备）...")
    iter_rows = [
        ('V1.0.0', '任务与执行基础', 'completed', -90, -55),
        ('V1.1.0', '报告与设备管理', 'completed', -50, -25),
        ('V2.0.0', '系统管理与消息', 'active', -20, 30),
    ]
    iteration_ids = []
    for name, goal, status, start_delta, end_delta in iter_rows:
        start_d = (now + timedelta(days=start_delta)).strftime(time_fmt)
        end_d = (now + timedelta(days=end_delta)).strftime(time_fmt)
        cursor.execute("""
            INSERT INTO iterations (project_id, iteration_name, description, goal, status, start_date, end_date, version, created_by, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (project_id, name, f'任务与设备 {name} 迭代', goal, status, start_d, end_d, name, uid_creator, uid_creator))
        iteration_ids.append(cursor.lastrowid)

    print("插入需求（任务与设备）...")
    req_rows = [
        ('测试任务管理', '任务CRUD、文件夹管理、用例快照', iteration_ids[0], 'completed'),
        ('手工执行', '逐条执行、状态标记、执行统计', iteration_ids[0], 'completed'),
        ('测试报告', '报告生成、详情、导出', iteration_ids[1], 'completed'),
        ('设备管理', '设备CRUD、ADB发现/指令、Agent桥接', iteration_ids[1], 'completed'),
        ('系统管理', '用户管理、角色权限、系统设置', iteration_ids[2], 'in_progress'),
        ('消息中心', '通知推送、已读管理、置顶清空', iteration_ids[2], 'in_progress'),
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

    print("插入用例库（任务与设备 功能模块）...")

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

    root_folder_id = _mk_folder_m('任务与设备用例库', '任务、报告、设备、系统、消息', None)
    f_task = _mk_folder_m('测试任务', '任务管理与执行', root_folder_id, 0)
    f_report = _mk_folder_m('测试报告', '报告生成与导出', root_folder_id, 1)
    f_device = _mk_folder_m('设备管理', '设备与Agent', root_folder_id, 2)
    f_system = _mk_folder_m('系统管理', '用户、角色、设置', root_folder_id, 3)
    f_message = _mk_folder_m('消息中心', '通知与推送', root_folder_id, 4)

    MODULES = [
        ('测试任务管理', requirement_ids[0], 18),
        ('手工执行', requirement_ids[1], 16),
        ('测试报告', requirement_ids[2], 14),
        ('设备管理', requirement_ids[3], 20),
        ('系统管理', requirement_ids[4], 18),
        ('消息中心', requirement_ids[5], 14),
    ]
    m_folder_map = {
        '测试任务管理': f_task, '手工执行': f_task,
        '测试报告': f_report, '设备管理': f_device,
        '系统管理': f_system, '消息中心': f_message,
    }
    m_extra = {
        '设备管理': ['设备CRUD用例集', 'Agent桥接用例集'],
        '系统管理': ['用户管理用例集', '角色权限用例集', '系统设置用例集'],
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

    TASK_CASES = {
        '测试任务管理': [
            ('创建测试任务', '任务名: 登录回归', '已有用例集', '点击新建任务，选择关联用例集，填写信息', '任务创建成功，列表出现', 'P0'),
            ('创建任务-必填校验', None, '新建任务页', '不填名称直接提交', '提示"任务名称不能为空"', 'P1'),
            ('任务关联用例集', None, '已有任务和用例集', '编辑任务，关联用例集', '任务详情显示关联的用例集', 'P0'),
            ('任务创建时生成用例快照', None, '关联的用例集有用例', '创建任务', '快照表记录当前用例版本', 'P0'),
            ('删除任务', None, '已有pending任务', '点击删除', '任务移除', 'P1'),
            ('删除已完成的任务', None, '任务状态completed', '点击删除', '提示确认后删除', 'P1'),
            ('任务文件夹管理', None, '任务列表', '新建任务文件夹', '文件夹创建成功', 'P1'),
            ('任务移动到文件夹', None, '有文件夹和任务', '拖拽任务到文件夹', '任务归入文件夹', 'P2'),
            ('任务列表筛选', '状态: pending', '有多个任务', '按状态筛选', '只显示pending任务', 'P1'),
            ('任务列表搜索', '关键词: 登录', '有多个任务', '搜索"登录"', '显示匹配任务', 'P2'),
        ],
        '手工执行': [
            ('开始执行任务', None, '任务状态pending', '点击开始执行', '任务状态变为running', 'P0'),
            ('逐条标记通过', None, '执行中有未执行用例', '点击某条用例的"通过"', '该用例标记pass', 'P0'),
            ('逐条标记失败', None, '执行中', '点击"失败"', '标记fail，可填备注', 'P0'),
            ('标记阻塞', None, '执行中', '点击"阻塞"', '标记blocked', 'P1'),
            ('标记不适用', None, '执行中', '点击"不适用"', '标记not_applicable', 'P1'),
            ('暂停执行', None, '任务running', '点击暂停', '任务暂停，保留已执行状态', 'P1'),
            ('继续执行', None, '任务已暂停', '点击继续', '恢复执行', 'P1'),
            ('完成执行', None, '所有用例已标记', '点击完成', '任务状态变completed', 'P0'),
            ('执行统计实时更新', None, '执行中', '标记几条用例后查看', '通过率实时刷新', 'P1'),
            ('执行中修改用例结果', None, '某用例已标pass', '重新标记为fail', '状态更新为fail', 'P2'),
            ('执行快照与当前用例版本对比', None, '快照后用例有修改', '查看执行页', '显示快照版本而非最新版', 'P2'),
        ],
        '测试报告': [
            ('完成任务自动生成报告', None, '任务刚标记completed', '查看报告列表', '出现该任务的报告', 'P0'),
            ('报告详情-执行汇总', None, '已有报告', '点击报告详情', '显示通过率、用例分布柱状图', 'P0'),
            ('报告详情-用例明细', None, '已有报告', '查看明细', '列出每条用例的执行状态', 'P0'),
            ('报告列表按项目筛选', None, '有多个项目报告', '选择项目筛选', '只显示该项目报告', 'P1'),
            ('导出Word报告', None, '已有报告', '点击导出Word', '下载.docx文件，内容正确', 'P1'),
            ('导出Excel报告', None, '已有报告', '点击导出Excel', '下载.xlsx文件', 'P1'),
            ('批量删除报告', None, '有多条报告', '勾选多条删除', '报告移除', 'P2'),
            ('无执行数据报告兜底', None, '任务completed但无执行记录', '查看报告', '显示空数据状态，不报错', 'P2'),
        ],
        '设备管理': [
            ('录入设备', '设备名: 华为P50', '已登录', '填写设备信息提交', '设备创建成功', 'P0'),
            ('编辑设备', None, '已有设备', '修改设备型号', '信息更新', 'P0'),
            ('删除设备', None, '设备无关联任务', '删除设备', '删除成功', 'P1'),
            ('ADB自动发现设备', None, 'Agent在线且有USB设备', '点击发现设备', '列表刷新，显示已连接设备', 'P0'),
            ('ADB发送指令', '指令: adb shell getprop', '设备在线', '选择设备，发送ADB指令', '返回指令输出', 'P1'),
            ('设备投屏', None, '设备在线', '点击投屏按钮', '打开scrcpy投屏窗口', 'P1'),
            ('设备列表搜索', '关键词: 华为', '有多台设备', '搜索"华为"', '显示匹配设备', 'P2'),
            ('批量分配设备', None, '有多台未分配设备', '勾选后分配给用户', '设备归属更新', 'P2'),
            ('Agent注册', None, 'Agent首次启动', 'Agent向平台上报注册', '平台显示新Agent', 'P0'),
            ('Agent绑定', None, '有未绑定的Agent', '输入绑定码绑定', '绑定成功', 'P0'),
            ('Agent解绑', None, '已绑定Agent', '解绑操作', 'Agent解绑成功', 'P1'),
            ('Agent心跳保活', None, 'Agent在线', 'Agent定期上报', '平台显示Agent在线状态', 'P1'),
            ('Agent离线检测', None, 'Agent在线', 'Agent断开超过心跳超时', '平台标记Agent离线', 'P1'),
            ('设备脚本异步调度', None, '设备在线，有脚本任务', '触发调度', '脚本在设备端执行', 'P1'),
        ],
        '系统管理': [
            ('新增用户', '用户名: newuser', '管理员登录', '填写用户信息提交', '用户创建成功', 'P0'),
            ('编辑用户', None, '已有用户', '修改用户信息', '更新成功', 'P0'),
            ('停用用户', None, '已有用户', '将用户停用', '用户无法登录', 'P0'),
            ('管理员重置他人密码', None, '管理员登录', '选择用户重置密码', '密码重置成功', 'P1'),
            ('角色分配', None, '已有用户', '修改用户角色为tester', '角色更新', 'P0'),
            ('权限配置-菜单可见性', None, '管理员', '配置某角色隐藏设备管理菜单', '该角色用户看不到设备管理', 'P1'),
            ('权限配置-操作控制', None, '管理员', '禁止tester删除项目', 'tester无法删除项目', 'P1'),
            ('全局配置-平台名称', '名称: 我的测试平台', '管理员', '修改平台名称', '页面标题更新', 'P2'),
            ('AI参数配置', 'API Key: sk-xxx', '管理员', '填写AI模型配置', '配置保存成功', 'P1'),
            ('个人设置-通知偏好', None, '已登录', '关闭邮件通知', '不再收到邮件通知', 'P2'),
            ('个人设置-界面偏好', None, '已登录', '切换主题色', '界面主题更新', 'P2'),
            ('非管理员访问系统设置', None, 'tester角色', '尝试访问系统管理页', '提示无权限或菜单不可见', 'P1'),
        ],
        '消息中心': [
            ('收到评审通知', None, '有人发起评审指定当前用户', '查看消息中心', '显示评审通知', 'P0'),
            ('收到AI生成完成通知', None, 'AI生成任务完成', '查看消息中心', '显示生成完成通知', 'P0'),
            ('实时推送-不刷新收到', None, '已登录', '其他用户发起评审', '页面实时弹出通知提示', 'P0'),
            ('单条已读', None, '有未读通知', '点击一条通知', '该通知标记已读', 'P0'),
            ('全部已读', None, '有多条未读', '点击全部已读', '所有通知变为已读', 'P1'),
            ('通知列表分类', None, '有不同类型通知', '查看列表', '按评审/AI/系统等分类显示', 'P1'),
            ('置顶通知', None, '有通知', '右键置顶', '该通知显示在列表顶部', 'P2'),
            ('清空全部通知', None, '有通知', '点击清空', '通知全部清除', 'P2'),
            ('通知跳转到详情', None, '有评审通知', '点击通知', '跳转到对应评审任务详情', 'P1'),
        ],
    }

    cases_data = []
    case_seq = 0
    cases_by_suite = {}
    for suite_id, proj_id, req_id, mod_name, _n in suite_rows:
        module_cases = TASK_CASES.get(mod_name, [])
        if not module_cases:
            continue
        suite_cases = []
        for c in module_cases:
            cname, td, pre, step, er, pri = c
            case_seq += 1
            case_number = f"TC-MTD-{case_seq:04d}"
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
    print(f"  共插入 {len(cases_data)} 条用例（任务与设备）")

    cursor.execute("SELECT id, suite_id, case_number FROM test_cases WHERE project_id = %s ORDER BY id", (project_id,))
    case_suite_map = {}
    case_id_by_number = {}
    for cid, sid, cnum in cursor.fetchall():
        case_suite_map.setdefault(sid, []).append(cid)
        case_id_by_number[cnum] = cid

    # ── 脑图 ──
    print("生成脑图数据并回写（任务与设备）...")
    for suite_id, proj_id, req_id, mod_name, _n in suite_rows:
        module_cases = TASK_CASES.get(mod_name, [])
        suite_case_tuples = cases_by_suite.get(suite_id, [])
        if not module_cases:
            continue
        root_children = []
        for idx, c in enumerate(module_cases):
            cname, td, pre, step, er, pri = c
            case_number = suite_case_tuples[idx][0] if idx < len(suite_case_tuples) else f'TC-MTD-{idx+1:04d}'
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

    # ── 标签标记 ──
    print("插入标签和标记（任务与设备）...")
    tag_data = [
        ('任务核心', '#67C23A', project_id, uid_creator),
        ('设备专项', '#E6A23C', project_id, uid_creator),
        ('系统管理', '#409EFF', project_id, uid_creator),
    ]
    cursor.executemany(
        "INSERT INTO case_tags (tag_name, tag_color, project_id, creator_id) VALUES (%s,%s,%s,%s)",
        tag_data)
    for name in ['待验证', '已修复', '暂不处理']:
        cursor.execute(
            "INSERT INTO case_markers (marker_name, marker_type, project_id, creator_id) VALUES (%s,%s,%s,%s)",
            (name, 'custom', project_id, uid_creator))

    # ── 测试任务 & 执行 ──
    cursor.execute("SELECT id FROM task_folders WHERE task_type = 'test_case' ORDER BY sort_order LIMIT 1")
    folder_row = cursor.fetchone()
    folder_id = folder_row[0] if folder_row else None

    print("插入测试任务（任务与设备）...")
    suite_id_to_name = {r[0]: r[3] for r in suite_rows}
    for idx, row in enumerate(suite_rows[:3]):
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
            f'【用例】{mod_name}', f'任务与设备管理 {mod_name} 用例执行', folder_id, 'test_case', 'high',
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

    # ── 报告 ──
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
            task_id, task_type, task_name, proj_id, '任务与设备', json.dumps(summary), json.dumps(details), completed_at, uid_creator, uid_tester1,
            'completed', None, suite_id, suite_name_snap, req_name,
        ))

    print("任务与设备 业务数据插入完成。")
    return True


# =====================================================================
# 主入口
# =====================================================================

def insert_test_data():
    """插入测试数据：用户 + 用例与项目 + 任务与设备 模拟数据。"""
    connection = get_db_connection()
    if not connection:
        return False

    try:
        with connection.cursor() as cursor:
            print("开始清空现有数据...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            tables = [
                'reports', 'notifications', 'user_settings', 'system_settings',
                'test_case_review_history', 'test_suite_review_history',
                'test_case_review_details', 'test_suite_review_tasks',
                'task_case_snapshots', 'task_device_relation',
                'task_case_relation', 'test_case_executions',
                'test_tasks', 'task_folders',
                'case_tags', 'case_markers', 'test_cases',
                'mindmap_versions', 'test_suites',
                'version_requirements', 'iterations',
                'project_members', 'projects', 'devices',
                'agent_binding_codes', 'user_agent_bindings', 'agents',
                'role_permissions', 'email_verify_codes', 'users',
            ]
            for table in tables:
                cursor.execute(f"TRUNCATE TABLE {table}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            print("现有数据清空完成！")

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

        if not insert_case_and_project_data(connection):
            return False
        if not insert_task_and_device_data(connection):
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
    print("开始插入测试数据（用户 + 用例与项目 + 任务与设备）...")
    if insert_test_data():
        print("测试数据插入完成！")
    else:
        print("测试数据插入失败！")


if __name__ == '__main__':
    main()
