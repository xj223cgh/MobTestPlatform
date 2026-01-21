import os
import uuid
import hashlib
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

files_bp = Blueprint('files', __name__)

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    上传文件API，用于上传设备脚本文件
    """
    try:
        # 检查是否有文件被上传
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '请选择要上传的文件'}), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'code': 400, 'message': '文件名不能为空'}), 400
        
        # 检查文件类型
        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = current_app.config.get('ALLOWED_SCRIPT_EXTENSIONS', ['.sh', '.py'])
        if file_ext not in allowed_extensions:
            return jsonify({'code': 400, 'message': f"只允许上传 {', '.join(allowed_extensions)} 文件"}), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        max_size = current_app.config.get('MAX_SCRIPT_SIZE', 10 * 1024 * 1024)  # 默认10MB
        file.seek(0)
        
        if file_size > max_size:
            return jsonify({'code': 400, 'message': f'文件大小不能超过 {max_size / 1024 / 1024}MB'}), 400
        
        # 生成唯一文件名，避免命名冲突
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        secure_name = secure_filename(unique_filename)
        
        # 构建存储目录（按日期组织）
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        storage_dir = os.path.join(current_app.config['SCRIPT_STORAGE_PATH'], date_str)
        
        # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)
        
        # 构建完整的存储路径
        file_path = os.path.join(storage_dir, secure_name)
        relative_path = os.path.join(date_str, secure_name)  # 相对路径，用于存储到数据库
        
        # 保存文件
        file.save(file_path)
        
        # 计算文件哈希值（用于验证文件完整性）
        file_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                file_hash.update(chunk)
        file_hash_str = file_hash.hexdigest()
        
        # 返回文件元数据
        return jsonify({
            'code': 200,
            'message': '文件上传成功',
            'data': {
                'filename': file.filename,
                'unique_filename': secure_name,
                'file_path': relative_path,
                'file_hash': file_hash_str,
                'file_size': file_size,
                'file_ext': file_ext
            }
        })
    except Exception as e:
        current_app.logger.error(f'文件上传失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'文件上传失败: {str(e)}'}), 500

@files_bp.route('/<path:file_path>', methods=['GET'])
def get_file(file_path):
    """
    下载文件
    """
    try:
        # 构建完整的文件路径
        full_path = os.path.join(current_app.config['SCRIPT_STORAGE_PATH'], file_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            return jsonify({'code': 404, 'message': '文件不存在'}), 404
        
        # 使用send_from_directory实现文件下载
        from flask import send_from_directory
        
        # 获取文件目录和文件名
        file_dir = os.path.dirname(full_path)
        server_filename = os.path.basename(full_path)
        
        # 检查查询参数中是否有自定义文件名
        download_filename = server_filename  # 默认使用服务器上的文件名
        custom_filename = request.args.get('filename')
        if custom_filename:
            download_filename = custom_filename
        
        # 返回文件下载响应，使用自定义文件名
        return send_from_directory(file_dir, server_filename, as_attachment=True, download_name=download_filename)
    except Exception as e:
        current_app.logger.error(f'获取文件失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'获取文件失败: {str(e)}'}), 500

@files_bp.route('/<path:file_path>', methods=['DELETE'])
def delete_file(file_path):
    """
    删除文件
    """
    try:
        # 构建完整的文件路径
        full_path = os.path.join(current_app.config['SCRIPT_STORAGE_PATH'], file_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            return jsonify({'code': 404, 'message': '文件不存在'}), 404
        
        # 删除文件
        os.remove(full_path)
        
        return jsonify({'code': 200, 'message': '文件删除成功'})
    except Exception as e:
        current_app.logger.error(f'删除文件失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'删除文件失败: {str(e)}'}), 500
