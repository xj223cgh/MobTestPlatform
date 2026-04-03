"""
一键导入知识库脚本
用法: 在 backend/ 目录下运行
  python -m app.config.knowledge.load_knowledge          # 导入 sample_docs 下所有文档
  python -m app.config.knowledge.load_knowledge --clear   # 先清空知识库再导入
"""
import sys
import os
import argparse
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent / 'sample_docs'
SUPPORTED_EXT = {'.md', '.txt', '.docx'}


def main():
    parser = argparse.ArgumentParser(description='批量导入知识库文档')
    parser.add_argument('--clear', action='store_true', help='导入前清空已有知识库数据')
    parser.add_argument('--dir', type=str, default=str(SAMPLE_DIR), help='文档目录路径')
    args = parser.parse_args()

    doc_dir = Path(args.dir)
    if not doc_dir.exists():
        print(f'[ERROR] 文档目录不存在: {doc_dir}')
        sys.exit(1)

    files = sorted(f for f in doc_dir.iterdir() if f.suffix.lower() in SUPPORTED_EXT)
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

    success, fail = 0, 0
    for f in files:
        try:
            content = f.read_bytes()
            result = upload_document(
                file_content=content,
                filename=f.name,
                metadata={'source': 'batch_import'},
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
