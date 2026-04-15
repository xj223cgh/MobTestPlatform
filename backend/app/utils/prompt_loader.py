"""提示词模板加载器：从 YAML 读取配置，使用 Jinja2 渲染，支持基于文件修改时间的热加载。"""
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / 'ai' / 'prompts'
_cache: dict = {}
_mtimes: dict = {}

_DEFAULT_SYSTEM = (
    "你是专业测试工程师。根据用户提供的需求文档生成测试用例时，必须严格依据文档内容：\n"
    "- 每条用例的步骤和预期结果需与文档中的描述对应，不编造文档未提及的功能或规则。\n"
    "- 按功能点/场景完整覆盖，需求多则用例数量应相应增加，不要人为限制在固定条数。\n"
    "- 只输出用户要求的 JSON，不要输出任何解释、代码块标记或多余文字。"
)


def _load_yaml(filename: str) -> dict:
    """加载 YAML 文件，基于修改时间缓存避免重复解析。"""
    filepath = _PROMPTS_DIR / filename
    if not filepath.exists():
        return {}
    mtime = filepath.stat().st_mtime
    if filename in _cache and _mtimes.get(filename) == mtime:
        return _cache[filename]
    import yaml
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    _cache[filename] = data
    _mtimes[filename] = mtime
    return data


def load_system_prompt(filename: str = 'system.yaml') -> str:
    """加载系统角色提示词；文件缺失时使用内置默认值。"""
    data = _load_yaml(filename)
    return data.get('content', '').strip() or _DEFAULT_SYSTEM


def render_prompt(filename: str, **kwargs) -> str:
    """从 YAML 加载 Jinja2 模板并用 kwargs 渲染为最终提示词。"""
    data = _load_yaml(filename)
    template_str = data.get('template', '')
    if not template_str:
        raise FileNotFoundError(f"Prompt template not found or empty: {filename}")
    from jinja2 import Template
    return Template(template_str).render(**kwargs)
