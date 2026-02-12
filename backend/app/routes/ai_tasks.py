"""
AI异步任务接口
用于处理AI自动生成测试用例的异步任务
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.models import db, TestSuite, TestCase, User
from app.utils.helpers import success_response, error_response
from app.utils.task_manager import task_manager, TaskStatus
import requests
import json
import os

# 创建Blueprint
bp = Blueprint('ai_tasks', __name__, url_prefix='/api/ai-tasks')


def generate_test_cases_task(suite_id: int, params: dict, task_manager, task_id: str):
    """
    AI生成测试用例的异步任务（在后台线程中运行，需在应用上下文中执行数据库等操作）
    
    Args:
        suite_id: 用例集ID
        params: 生成参数（含 _app 用于推入应用上下文）
        task_manager: 任务管理器
        task_id: 任务ID
        
    Returns:
        生成结果
    """
    app = params.pop('_app', None)
    if not app:
        raise RuntimeError("缺少应用上下文，无法在后台执行任务")
    
    with app.app_context():
        try:
            # 更新进度：开始解析文档
            task_manager.update_task_status(
                task_id,
                message='正在解析需求文档...',
                progress=10
            )
            
            # 1. 解析需求文档内容（从前端传来的documentContent）
            document_content = params.get('documentContent', '')
            
            # 更新进度：构建提示词
            task_manager.update_task_status(
                task_id,
                message='正在构建AI提示词...',
                progress=20
            )
            
            # 2. 构建AI提示词
            prompt = build_test_case_prompt(params, document_content)
            
            # 更新进度：调用AI接口
            task_manager.update_task_status(
                task_id,
                message='正在调用AI生成用例...',
                progress=30
            )
            
            # 3. 调用AI接口生成测试用例（长文档时提高 max_tokens 避免结果被截断）
            ai_config = get_ai_config()
            doc_len = len(document_content or '')
            base_max = ai_config.get('maxTokens', 4096)
            extra_tokens = min(12288, (doc_len // 1000) * 500)
            dynamic_max_tokens = min(16384, base_max + extra_tokens)
            ai_response = call_ai_api(prompt, ai_config, max_tokens_override=dynamic_max_tokens)
            
            # 更新进度：解析AI返回结果
            task_manager.update_task_status(
                task_id,
                message='正在解析AI返回结果...',
                progress=50
            )
            
            # 4. 解析AI返回的用例数据
            test_cases = parse_ai_response(ai_response)
            
            if not test_cases:
                raise Exception("AI未生成任何测试用例")
            
            # 更新进度：准备保存用例
            task_manager.update_task_status(
                task_id,
                message=f'正在保存测试用例，共{len(test_cases)}条...',
                progress=60
            )
            
            # 5. 加载用例集并取 project_id/iteration_id/version_requirement_id
            suite = TestSuite.query.get(suite_id)
            if not suite:
                raise Exception("用例集不存在")
            project_id = params.get('projectId') or suite.project_id
            iteration_id = params.get('iterationId') or suite.iteration_id
            version_requirement_id = params.get('requirementId') or suite.version_requirement_id
            if project_id is None:
                raise ValueError("用例集未关联项目，无法保存测试用例。请为用例集选择所属项目。")
            
            # 6. 生成用例编号前缀（格式与前端一致：xxx-xxx-xxx，从 params 或 suite 关联取项目/迭代/需求名）
            case_number_prefix = generate_case_number_prefix(suite, params)
            
            # 7. 获取当前用例集中最大编号的尾号（格式 xxx-xxx-xxx001，取最后 3 位数字 001～999）
            max_index = get_max_case_index(suite_id)
            
            # 8. 批量保存测试用例
            saved_cases = []
            total_cases = len(test_cases)
            
            for i, case_item in enumerate(test_cases):
                # 更新进度
                current_progress = 60 + int((i / total_cases) * 35)
                task_manager.update_task_status(
                    task_id,
                    message=f'正在保存第{i+1}/{total_cases}条用例...',
                    progress=current_progress,
                    current=i+1,
                    total=total_cases
                )
                
                # 生成用例编号（原格式：xxx-xxx-xxx001，三段前缀 + 3 位数字 001～999）
                current_index = max_index + i + 1
                suffix = str(current_index).zfill(3)
                if current_index > 999:
                    suffix = "999"  # API 仅允许 001-999
                case_number = f"{case_number_prefix}{suffix}"
                
                # 构建用例数据（project_id 必填，从 params 或 suite 取）
                case_data = {
                    'suite_id': suite_id,
                    'case_number': case_number,
                    'case_name': case_item.get('case_name', f'测试用例_{case_number}'),
                    'case_description': case_item.get('case_description', ''),
                    'priority': case_item.get('priority', 'P1'),
                    'status': case_item.get('status', ''),
                    'preconditions': case_item.get('preconditions', ''),
                    'steps': case_item.get('steps', ''),
                    'expected_result': case_item.get('expected_result', ''),
                    'test_data': case_item.get('test_data', ''),
                    'project_id': project_id,
                    'iteration_id': iteration_id,
                    'version_requirement_id': version_requirement_id,
                    'creator_id': params.get('creatorId'),
                }
                
                # 保存用例到数据库
                test_case = TestCase(**case_data)
                db.session.add(test_case)
                saved_cases.append(case_data)
            
            # 提交事务
            db.session.commit()
            
            # 更新进度：完成
            task_manager.update_task_status(
                task_id,
                message=f'成功生成并保存{len(saved_cases)}条测试用例',
                progress=100
            )
            
            return {
                'suite_id': suite_id,
                'total_cases': len(saved_cases),
                'saved_cases': saved_cases[:5]  # 只返回前5条用例的预览
            }
            
        except Exception as e:
            db.session.rollback()
            raise e


def _suggest_case_count(document_content: str) -> int:
    """
    根据需求文档长度，估算建议生成的用例条数（用于提示词，不硬性限制）。
    原则：需求越大、功能点越多，用例数应越多。
    """
    text_len = len((document_content or '').strip())
    if text_len <= 0:
        return 10
    # 约每 300 字 建议若干条用例，最少 8 条，最多 80 条
    suggested = max(8, min(80, (text_len // 300) * 3))
    return suggested


def build_test_case_prompt(params: dict, document_content: str) -> str:
    """构建AI提示词：仅依据传入的需求文档内容生成用例，与用例集的所属项目/迭代/需求等元数据无关"""
    suggested_count = _suggest_case_count(document_content)
    doc_content = (document_content or '').strip()
    if not doc_content:
        doc_content = "（未提供需求文档内容）"

    prompt = f"""你是一名专业测试工程师。请**严格依据**下方「需求文档内容」生成功能测试用例。
每条用例的步骤、预期结果必须能在需求文档中找到对应依据，不要编造需求中未提及的行为。
（与用例集所属的项目、迭代、需求等无关，仅以需求文档内容为准。）

【需求文档内容】
{doc_content}

【输出要求】
1. 以 JSON 格式返回，且只返回 JSON，不要有任何其他说明文字。
2. 格式如下：
{{
  "test_cases": [
    {{
      "case_name": "用例名称",
      "case_description": "用例描述",
      "priority": "P0/P1/P2/P3/P4",
      "preconditions": "前置条件",
      "steps": "测试步骤（每步一行，可执行、可验证）",
      "expected_result": "预期结果（可验证、与需求对应）",
      "test_data": "测试数据"
    }}
  ]
}}

【质量与数量要求】
- 优先级：P0 最高，P4 最低；核心流程用 P0/P1，异常/边界用 P2/P3。
- 覆盖：对文档中的每个功能点/场景，至少生成正常流程、异常或边界类用例，不要遗漏重要功能。
- 数量：根据需求文档中的功能点数量决定，建议本需求生成约 **{suggested_count}～{suggested_count + 10}** 条用例；若功能点很多可超过该范围，确保完整覆盖。
- 步骤与结果：测试步骤要具体、可执行；预期结果要可验证，并与需求描述一致。
- 只输出上述 JSON，不要输出 ```json 以外的标记或解释。
"""
    return prompt


# 系统角色提示，约束 AI 严格按需求输出、不编造
SYSTEM_ROLE_CONTENT = """你是专业测试工程师。根据用户提供的需求文档生成测试用例时，必须严格依据文档内容：
- 每条用例的步骤和预期结果需与文档中的描述对应，不编造文档未提及的功能或规则。
- 按功能点/场景完整覆盖，需求多则用例数量应相应增加，不要人为限制在固定条数。
- 只输出用户要求的 JSON，不要输出任何解释、代码块标记或多余文字。"""


def call_ai_api(prompt: str, ai_config: dict, max_tokens_override: int = None) -> dict:
    """调用AI接口（OpenAI 兼容），支持动态 max_tokens 与 system 角色"""
    api_key = (ai_config.get('apiKey') or '').strip()
    if not api_key or api_key == 'sk-your-api-key' or api_key == 'sk-your-api-key-here':
        raise ValueError(
            '未配置有效的 AI_API_KEY。请在 backend/.env 中设置 AI_API_KEY，'
            '并到 SiliconFlow 控制台申请/复制密钥：https://cloud.siliconflow.cn/'
        )
    base_url = (ai_config.get('baseURL') or '').strip().rstrip('/')
    url = f"{base_url}/chat/completions"
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json'
    }
    max_tokens = max_tokens_override if max_tokens_override is not None else ai_config.get('maxTokens', 4096)
    data = {
        'model': ai_config.get('model', 'Qwen/Qwen2.5-7B-Instruct'),
        'messages': [
            {'role': 'system', 'content': SYSTEM_ROLE_CONTENT},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': ai_config.get('temperature', 0.3),
        'max_tokens': max_tokens
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        if response.status_code == 401:
            raise ValueError(
                'AI 服务认证失败(401)。请检查 backend/.env 中的 AI_API_KEY 是否有效、未过期，'
                '并到 SiliconFlow 控制台确认密钥状态：https://cloud.siliconflow.cn/'
            )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            raise ValueError(
                'AI 服务认证失败(401)。请检查 backend/.env 中的 AI_API_KEY 是否有效、未过期。'
            ) from e
        raise


def parse_ai_response(ai_response: dict) -> list:
    """解析AI返回结果"""
    try:
        content = ai_response['choices'][0]['message']['content']
        
        # 清理可能的markdown代码块标记
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        # 解析JSON
        parsed = json.loads(content)
        return parsed.get('test_cases', [])
    except Exception as e:
        raise Exception(f"解析AI返回结果失败: {str(e)}")


def _ensure_env_loaded():
    """确保已从 backend/.env 加载环境变量（后台线程或未经过 run.py 时可能未加载）"""
    from pathlib import Path
    api_key = (os.getenv('AI_API_KEY') or '').strip()
    if api_key and api_key not in ('sk-your-api-key', 'sk-your-api-key-here'):
        return
    _backend_dir = Path(__file__).resolve().parent.parent.parent  # routes -> app -> backend
    _env_file = _backend_dir / '.env'
    if _env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_env_file, override=True)


def get_ai_config() -> dict:
    """获取AI配置（从环境变量读取，自动去除首尾空格）"""
    _ensure_env_loaded()
    api_key = (os.getenv('AI_API_KEY') or 'sk-your-api-key').strip()
    base_url = (os.getenv('AI_BASE_URL') or 'https://api.siliconflow.cn/v1').strip().rstrip('/')
    return {
        'baseURL': base_url,
        'apiKey': api_key,
        'model': (os.getenv('AI_MODEL') or 'Qwen/Qwen2.5-7B-Instruct').strip(),
        'temperature': float(os.getenv('AI_TEMPERATURE', '0.3')),
        'maxTokens': int(os.getenv('AI_MAX_TOKENS', '4096'))
    }


# 常用中文→英文（用于用例编号：取英文单词首字母）
# 优先 2 字词，再 1 字；英文取各单词首字母，如 "User Management" -> "UM"
_ZH2EN = {
    "项目": "Project", "用户": "User", "管理": "Management", "需求": "Requirement",
    "登录": "Login", "系统": "System", "测试": "Test", "模块": "Module", "功能": "Function",
    "平台": "Platform", "版本": "Version", "迭代": "Iteration", "接口": "Interface",
    "服务": "Service", "后台": "Backend", "前端": "Frontend", "数据": "Data",
    "订单": "Order", "支付": "Payment", "消息": "Message", "配置": "Config",
    "权限": "Permission", "角色": "Role", "审核": "Review", "报表": "Report",
    "文件": "File", "上传": "Upload", "下载": "Download", "搜索": "Search",
    "列表": "List", "详情": "Detail", "新增": "Create", "编辑": "Edit", "删除": "Delete",
    "移动": "Mobile", "网页": "Web", "应用": "Application", "中心": "Center",
    "个人": "Personal", "账户": "Account", "设置": "Settings", "首页": "Home",
    "单": "Single", "新": "New", "旧": "Old", "中": "Center", "心": "Core",
    "项": "Project", "目": "Item", "用": "Use", "户": "User", "需": "Requirement",
    "求": "Demand", "登": "Login", "录": "Record", "测": "Test", "试": "Test",
    "模": "Module", "块": "Block", "功": "Function", "能": "Capability",
    "系": "System", "统": "System", "版": "Version", "本": "Version",
}


def _english_word_initials(english_phrase: str) -> str:
    """取英文短语中各单词的首字母，如 'User Management' -> 'UM'"""
    if not english_phrase or not english_phrase.strip():
        return ""
    return "".join(w[0].upper() for w in english_phrase.strip().split() if w and w[0].isalpha())


def _chinese_char_to_pinyin_initial(char: str) -> str:
    """单个汉字转拼音首字母，无法转换时返回空字符串"""
    if not char or not ("\u4e00" <= char <= "\u9fff"):
        return ""
    try:
        from pypinyin import pinyin, Style
        py = pinyin(char, style=Style.FIRST_LETTER)
        if py and py[0] and py[0][0]:
            return py[0][0].upper()
    except Exception:
        pass
    return ""


def _name_to_english_abbrev(name: str, max_len: int = 3) -> str:
    """
    将名称转为缩写：中文按词典翻译成英文，再取英文各单词首字母；英文/数字保留。
    用于用例编号前缀，避免编号中出现中文。
    """
    if not name or not str(name).strip():
        return ""
    name = str(name).strip()
    result = []
    i = 0
    while i < len(name):
        char = name[i]
        if char.isalnum() or ord(char) < 128:
            result.append(char.upper())
            i += 1
            continue
        if "\u4e00" <= char <= "\u9fff":
            # 优先匹配 2 字词，再 1 字；无法翻译时用拼音首字母
            two = name[i : i + 2] if i + 2 <= len(name) else ""
            one = char
            if two and two in _ZH2EN:
                initials = _english_word_initials(_ZH2EN[two])
                result.append(initials)
                i += 2
            elif one in _ZH2EN:
                initials = _english_word_initials(_ZH2EN[one])
                result.append(initials)
                i += 1
            else:
                # 词典无该词，采用拼音缩写
                py = _chinese_char_to_pinyin_initial(one)
                if py:
                    result.append(py)
                if two:
                    py2 = _chinese_char_to_pinyin_initial(two[1])
                    if py2:
                        result.append(py2)
                    i += 2
                else:
                    i += 1
            continue
        i += 1
    abbrev = "".join(result)[:max_len]
    return abbrev if abbrev else ""


def generate_case_number_prefix(suite, params: dict) -> str:
    """
    生成用例编号前缀，与前端及 test_cases 接口一致：xxx-xxx-xxx（三段用横线连接）。
    名称中的中文按词典翻译为英文，再取英文单词首字母；纯英文/数字保留。
    """
    import re
    project_name = params.get("projectName") or (suite.project.project_name if suite.project else "") or "PROJ"
    iteration_name = params.get("iterationName") or (suite.iteration.iteration_name if suite.iteration else "") or "1.0.0"
    requirement_name = params.get("requirementName") or (suite.version_requirement.requirement_name if suite.version_requirement else "") or "REQ"

    # 项目缩写：中文→英文翻译→单词首字母，至多 3 位
    project_short = _name_to_english_abbrev(project_name, 3) or "PROJ"
    # 迭代版本号（x.y.z）
    version_match = re.search(r"\d+\.\d+\.\d+", str(iteration_name))
    version = version_match.group(0) if version_match else "1.0.0"
    # 需求缩写：中文→英文翻译→单词首字母，至多 3 位
    requirement_short = _name_to_english_abbrev(requirement_name, 3) or "REQ"

    return f"{project_short}-{version}-{requirement_short}"


def get_max_case_index(suite_id: int) -> int:
    """
    获取用例集中已有用例编号的最大尾号（数字部分）。
    编号格式为 xxx-xxx-xxx001，只取末尾 3 位数字，用于生成下一个 001～999 的序号。
    """
    import re
    try:
        cases = TestCase.query.filter_by(suite_id=suite_id).all()
        if not cases:
            return 0
        max_index = 0
        for case in cases:
            match = re.search(r'(\d{3})$', case.case_number or '')
            if match:
                index = int(match.group(1))
                max_index = max(max_index, index)
        return max_index
    except Exception:
        return 0


@bp.route('/generate-cases', methods=['POST'])
@login_required
def generate_cases():
    """
    创建AI生成测试用例的异步任务
    
    请求参数：
    {
        "suite_id": 用例集ID,
        "projectId": 项目ID,
        "iterationId": 迭代ID,
        "requirementId": 需求ID,
        "projectName": 项目名称,
        "iterationName": 迭代名称,
        "requirementName": 需求名称,
        "description": 需求描述,
        "documentContent": 需求文档内容
    }
    
    返回：
    {
        "code": 200,
        "data": {
            "task_id": "任务ID"
        }
    }
    """
    try:
        data = request.get_json()
        
        # 验证必填参数
        suite_id = data.get('suite_id')
        if not suite_id:
            return error_response('缺少用例集ID', 400)
        
        # 验证用例集是否存在
        suite = TestSuite.query.get(suite_id)
        if not suite:
            return error_response('用例集不存在', 404)
        
        # 准备任务参数（传入 app 供后台线程使用应用上下文）
        params = {
            '_app': current_app._get_current_object(),
            'projectId': data.get('projectId'),
            'iterationId': data.get('iterationId'),
            'requirementId': data.get('requirementId'),
            'projectName': data.get('projectName', ''),
            'iterationName': data.get('iterationName', ''),
            'requirementName': data.get('requirementName', ''),
            'description': data.get('description', ''),
            'documentContent': data.get('documentContent', ''),
            'creatorId': current_user.id,
        }
        
        # 创建异步任务
        task_id = task_manager.create_task(
            task_name=f'AI生成测试用例 - {suite.suite_name}',
            task_func=generate_test_cases_task,
            suite_id=suite_id,
            params=params
        )
        
        return success_response({
            'task_id': task_id,
            'suite_id': suite_id,
            'message': '任务已创建，正在后台生成测试用例'
        })
        
    except Exception as e:
        return error_response(f'创建任务失败: {str(e)}', 500)


@bp.route('/task-status/<task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
    """
    查询任务状态
    
    返回：
    {
        "code": 200,
        "data": {
            "task_id": "任务ID",
            "status": "pending|running|completed|failed",
            "progress": 进度百分比,
            "message": "状态消息",
            "result": 任务结果（仅completed状态）,
            "error": 错误信息（仅failed状态）
        }
    }
    """
    try:
        task_status = task_manager.get_task_status(task_id)
        
        if not task_status:
            return error_response('任务不存在', 404)
        
        return success_response(task_status)
        
    except Exception as e:
        return error_response(f'查询任务状态失败: {str(e)}', 500)


@bp.route('/tasks', methods=['GET'])
@login_required
def get_all_tasks():
    """
    获取所有任务列表（用于管理和调试）
    
    返回：
    {
        "code": 200,
        "data": [任务列表]
    }
    """
    try:
        # 获取所有任务
        all_tasks = list(task_manager.tasks.values())
        
        # 按创建时间倒序排序
        all_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return success_response(all_tasks)
        
    except Exception as e:
        return error_response(f'获取任务列表失败: {str(e)}', 500)
