"""Knowledge base API: document upload, list, delete, search."""
from flask import Blueprint, request
from flask_login import login_required
from app.utils.helpers import success_response, error_response

bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')


@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload and index a document into the knowledge base."""
    try:
        if 'file' not in request.files:
            return error_response(400, '缺少文件')
        file = request.files['file']
        if not file.filename:
            return error_response(400, '文件名为空')

        from app.services.knowledge_service import upload_document
        result = upload_document(
            file_content=file.read(),
            filename=file.filename,
            metadata={'uploaded_by': request.form.get('uploaded_by', '')},
        )
        return success_response(result)
    except (ValueError, RuntimeError) as e:
        return error_response(400, str(e))
    except Exception as e:
        return error_response(500, f'上传失败: {str(e)}')


@bp.route('/list', methods=['GET'])
@login_required
def list_docs():
    """List all indexed documents."""
    try:
        from app.services.knowledge_service import list_documents
        return success_response(list_documents())
    except Exception as e:
        return error_response(500, f'查询失败: {str(e)}')


@bp.route('/delete/<doc_id>', methods=['DELETE'])
@login_required
def delete(doc_id):
    """Delete a document and all its chunks from the knowledge base."""
    try:
        from app.services.knowledge_service import delete_document
        ok = delete_document(doc_id)
        if not ok:
            return error_response(404, '文档不存在')
        return success_response({'deleted': True})
    except Exception as e:
        return error_response(500, f'删除失败: {str(e)}')


@bp.route('/search', methods=['POST'])
@login_required
def search_kb():
    """Search the knowledge base for relevant chunks (debug endpoint)."""
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        if not query:
            return error_response(400, '缺少查询内容')
        top_k = data.get('top_k', 5)
        from app.services.knowledge_service import search
        results = search(query, top_k=top_k)
        return success_response(results)
    except Exception as e:
        return error_response(500, f'检索失败: {str(e)}')
