"""
知识库批量导入脚本（支持分类目录）

用法: 在 backend/ 目录下运行
  python -m app.ai.knowledge.load_knowledge               # 导入所有分类文档
  python -m app.ai.knowledge.load_knowledge --clear        # 先清空再导入
  python -m app.ai.knowledge.load_knowledge --category 01_core_business  # 只导入指定分类
  python -m app.ai.knowledge.load_knowledge --dir /path/to/docs          # 导入指定目录
"""
import sys
import argparse
from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parent / 'docs'
SUPPORTED_EXT = {'.md', '.txt', '.docx'}

CATEGORY_ORDER = [
    '01_core_business',
    '02_test_standards',
    '03_platform_config',
    '04_issue_cases',
    '05_test_guides',
]

CATEGORY_LABELS = {
    '01_core_business':   '核心业务知识',
    '02_test_standards':  '测试标准',
    '03_platform_config': '配置说明',
    '04_issue_cases':     '问题案例',
    '05_test_guides':     '测试指南',
}


def _collect_files(base_dir: Path, category: str = None) -> list:
    """收集待导入的文件列表，按分类优先级排序。"""
    files = []
    if category:
        cat_dir = base_dir / category
        if not cat_dir.exists():
            print(f'[ERROR] 分类目录不存在: {cat_dir}')
            sys.exit(1)
        for f in sorted(cat_dir.iterdir()):
            if f.suffix.lower() in SUPPORTED_EXT:
                files.append((category, f))
    else:
        for cat in CATEGORY_ORDER:
            cat_dir = base_dir / cat
            if not cat_dir.exists():
                continue
            for f in sorted(cat_dir.iterdir()):
                if f.suffix.lower() in SUPPORTED_EXT:
                    files.append((cat, f))
        loose = sorted(f for f in base_dir.iterdir()
                       if f.is_file() and f.suffix.lower() in SUPPORTED_EXT)
        for f in loose:
            files.append(('uncategorized', f))
    return files


def main():
    parser = argparse.ArgumentParser(description='批量导入知识库文档（支持分类）')
    parser.add_argument('--clear', action='store_true', help='导入前清空已有知识库数据')
    parser.add_argument('--dir', type=str, default=str(DOCS_ROOT), help='文档根目录路径')
    parser.add_argument('--category', type=str, default=None,
                        choices=CATEGORY_ORDER,
                        help='只导入指定分类')
    args = parser.parse_args()

    doc_dir = Path(args.dir)
    if not doc_dir.exists():
        print(f'[ERROR] 文档目录不存在: {doc_dir}')
        sys.exit(1)

    files = _collect_files(doc_dir, args.category)
    if not files:
        print(f'[WARN] 目录下无可导入文档: {doc_dir}')
        sys.exit(0)

    from app.services.knowledge_service import upload_document, list_documents, delete_document

    if args.clear:
        print('[INFO] 正在清空知识库...')
        existing = list_documents()
        for doc in existing:
            delete_document(doc['doc_id'])
        print(f'[INFO] 已清除 {len(existing)} 份文档')

    print(f'[INFO] 共发现 {len(files)} 个文档，开始导入...\n')

    current_cat = None
    success, fail = 0, 0

    for cat, f in files:
        if cat != current_cat:
            current_cat = cat
            label = CATEGORY_LABELS.get(cat, cat)
            print(f'\n── {label} ({cat}) ──')

        try:
            content = f.read_bytes()
            result = upload_document(
                file_content=content,
                filename=f.name,
                metadata={
                    'source': 'batch_import',
                    'category': cat,
                    'category_label': CATEGORY_LABELS.get(cat, ''),
                },
            )
            chunks = result['total_chunks']
            print(f'  [OK] {f.name}  →  {chunks} chunks')
            success += 1
        except Exception as e:
            print(f'  [FAIL] {f.name}  →  {e}')
            fail += 1

    print(f'\n[DONE] 成功: {success}, 失败: {fail}')

    total_docs = list_documents()
    print(f'[INFO] 知识库当前共 {len(total_docs)} 份文档')


if __name__ == '__main__':
    main()
