"""AI 测试用例生成模块 —— 统一目录入口。

目录结构：
    ai/
    ├── ai_config.yaml           # AI 角色、行为、知识检索策略配置
    ├── knowledge/               # 知识库
    │   ├── docs/                # 分类知识文档
    │   │   ├── 01_core_business/    必读核心业务知识 (8篇)
    │   │   ├── 02_test_standards/   测试标准与规范   (3篇)
    │   │   ├── 03_platform_config/  平台配置说明     (3篇)
    │   │   ├── 04_issue_cases/      历史问题案例     (2篇)
    │   │   └── 05_test_guides/      测试指南         (2篇)
    │   ├── chroma_data/         # ChromaDB 向量数据库
    │   └── load_knowledge.py    # 知识库批量导入脚本
    ├── prompts/                 # 提示词模板
    ├── workspace/               # 文档工作区
    │   ├── requirements/        # 需求文档 (original / converted)
    │   └── outputs/excel/       # 生成的用例 Excel 文件
    └── excel_exporter.py        # 用例 Excel 导出工具
"""
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parent
