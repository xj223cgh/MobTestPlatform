"""文件上传与下载：Logo 图片、设备脚本。"""
import os
import uuid
import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import login_required

from app.models.models import SystemSetting

files_bp = Blueprint('files', __name__)

LOGO_URL_PREFIX = '/api/files/logo/'


def _safe_join(base_dir, user_path):
    """将 user_path 限制在 base_dir 之内，防止路径穿越。"""
    resolved = os.path.normpath(os.path.join(base_dir, user_path))
    if not resolved.startswith(os.path.normpath(base_dir)):
        return None
    return resolved


def _delete_old_logo_if_exists():
    """删除数据库中记录的旧 Logo 文件（若存在且属于本机存储）。"""
    try:
        row = SystemSetting.query.filter_by(setting_key='system_logo').first()
        if not row or not row.setting_value or not row.setting_value.strip():
            return
        url = row.setting_value.strip()
        if not url.startswith(LOGO_URL_PREFIX):
            return
        subpath = url[len(LOGO_URL_PREFIX):].lstrip('/')
        if not subpath or '..' in subpath:
            return
        logo_dir = current_app.config['LOGO_STORAGE_PATH']
        full_path = os.path.join(logo_dir, subpath)
        if os.path.isfile(full_path):
            os.remove(full_path)
            current_app.logger.info(f'已删除旧 Logo 文件: {full_path}')
    except Exception as e:
        current_app.logger.warning(f'删除旧 Logo 文件时出错: {e}')


@files_bp.route('/upload/logo', methods=['POST'])
@login_required
def upload_logo():
    """
    上传系统 Logo。图片保存到服务端 LOGO_STORAGE_PATH，路径写入 system_settings 表。
    若已有 Logo，会先删除旧文件再保存新文件。
    """
    try:
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '请选择要上传的图片'}), 400
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'code': 400, 'message': '请选择要上传的图片'}), 400

        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed = current_app.config.get('ALLOWED_LOGO_EXTENSIONS', ['.jpg', '.jpeg', '.png'])
        if file_ext not in allowed:
            return jsonify({'code': 400, 'message': '仅支持 JPG、PNG 格式'}), 400

        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        max_size = current_app.config.get('MAX_LOGO_SIZE', 2 * 1024 * 1024)
        if size > max_size:
            return jsonify({'code': 400, 'message': '图片大小不能超过 2MB'}), 400

        logo_dir = current_app.config['LOGO_STORAGE_PATH']
        date_str = datetime.now().strftime('%Y%m%d')
        save_dir = os.path.join(logo_dir, date_str)
        os.makedirs(save_dir, exist_ok=True)

        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        safe_name = secure_filename(unique_name)
        full_path = os.path.join(save_dir, safe_name)
        relative_subpath = f"{date_str}/{safe_name}"

        _delete_old_logo_if_exists()
        file.save(full_path)

        new_url = f"{LOGO_URL_PREFIX}{relative_subpath}"
        # 仅保存文件并返回 URL，不写入数据库；持久化在用户点击「保存设置」时由 settings 接口完成
        return jsonify({
            'code': 200,
            'message': 'Logo 上传成功',
            'data': {'url': new_url}
        })
    except Exception as e:
        current_app.logger.error(f'Logo 上传失败: {e}')
        return jsonify({'code': 500, 'message': f'上传失败: {str(e)}'}), 500


@files_bp.route('/logo/<path:subpath>', methods=['GET'])
def get_logo(subpath):
    """根据数据库中的路径提供 Logo 图片访问。"""
    if not subpath or '..' in subpath:
        return jsonify({'code': 400, 'message': '无效路径'}), 400
    logo_dir = current_app.config['LOGO_STORAGE_PATH']
    full_path = os.path.join(logo_dir, subpath)
    if not os.path.isfile(full_path):
        return jsonify({'code': 404, 'message': '文件不存在'}), 404
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    return send_from_directory(directory, filename, mimetype=None, as_attachment=False)


@files_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """
    上传文件API，用于上传设备脚本文件
    """
    try:
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '请选择要上传的文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'code': 400, 'message': '文件名不能为空'}), 400
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = current_app.config.get('ALLOWED_SCRIPT_EXTENSIONS', ['.sh', '.py'])
        if file_ext not in allowed_extensions:
            return jsonify({'code': 400, 'message': f"只允许上传 {', '.join(allowed_extensions)} 文件"}), 400
        
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        max_size = current_app.config.get('MAX_SCRIPT_SIZE', 10 * 1024 * 1024)
        file.seek(0)
        
        if file_size > max_size:
            return jsonify({'code': 400, 'message': f'文件大小不能超过 {max_size / 1024 / 1024}MB'}), 400
        
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        secure_name = secure_filename(unique_filename)
        
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        storage_dir = os.path.join(current_app.config['SCRIPT_STORAGE_PATH'], date_str)
        os.makedirs(storage_dir, exist_ok=True)
        
        file_path = os.path.join(storage_dir, secure_name)
        relative_path = os.path.join(date_str, secure_name)
        
        file.save(file_path)
        
        file_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                file_hash.update(chunk)
        file_hash_str = file_hash.hexdigest()
        
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
@login_required
def get_file(file_path):
    """下载脚本文件"""
    try:
        base = current_app.config['SCRIPT_STORAGE_PATH']
        full_path = _safe_join(base, file_path)
        if not full_path or not os.path.isfile(full_path):
            return jsonify({'code': 404, 'message': '文件不存在'}), 404

        file_dir = os.path.dirname(full_path)
        server_filename = os.path.basename(full_path)
        download_filename = request.args.get('filename') or server_filename
        return send_from_directory(file_dir, server_filename, as_attachment=True, download_name=download_filename)
    except Exception as e:
        current_app.logger.error(f'获取文件失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'获取文件失败: {str(e)}'}), 500


@files_bp.route('/<path:file_path>', methods=['DELETE'])
@login_required
def delete_file(file_path):
    """删除脚本文件"""
    try:
        base = current_app.config['SCRIPT_STORAGE_PATH']
        full_path = _safe_join(base, file_path)
        if not full_path or not os.path.isfile(full_path):
            return jsonify({'code': 404, 'message': '文件不存在'}), 404

        os.remove(full_path)
        return jsonify({'code': 200, 'message': '文件删除成功'})
    except Exception as e:
        current_app.logger.error(f'删除文件失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'删除文件失败: {str(e)}'}), 500
