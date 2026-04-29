# 路由文件 - RESTful API 后端

from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from app import app
import os
import time
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, MAX_FILE_SIZE, MODEL_TYPE
from werkzeug.utils import secure_filename
import uuid
import mimetypes
from app.utils.logger import logger
from app.di.container import container

# 获取项目根目录（app/ 的上级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# MIME 类型白名单
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # docx
    'text/markdown',
    'text/plain',
    'application/octet-stream',  # 通用二进制文件（作为兜底）
}

# 统一响应函数，自动添加时间戳
def api_response(code: int, msg: str = '', data: dict = None) -> dict:
    """
    统一 API 响应格式
    
    Args:
        code: 状态码，0 表示成功，非 0 表示失败
        msg: 提示信息
        data: 数据内容
        
    Returns:
        统一格式的响应字典
    """
    response = {
        'code': code,
        'timestamp': int(time.time()),
        'msg': msg
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)

# 尝试加载现有文档并创建索引
def init_index(upload_dir):
    container.init_index(upload_dir)

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 验证文件路径安全性（防止路径遍历攻击）
def is_safe_path(base_path, filename):
    """验证文件路径是否安全，防止路径遍历攻击"""
    # 规范化路径
    abs_base = os.path.abspath(base_path)
    abs_target = os.path.abspath(os.path.join(base_path, filename))
    # 确保目标路径在允许的目录下
    return abs_target.startswith(abs_base + os.sep) or abs_target == abs_base

# 验证文件 MIME 类型
def validate_mime_type(file):
    """验证文件 MIME 类型是否允许"""
    # 从文件名推断 MIME 类型
    mime_type, _ = mimetypes.guess_type(file.filename)
    
    # 如果能正确识别 MIME 类型，进行验证
    if mime_type and mime_type in ALLOWED_MIME_TYPES:
        return True
    
    # 如果无法识别 MIME 类型，回退到检查文件扩展名
    # 这处理了 mimetypes 模块无法识别某些文件类型的情况
    if allowed_file(file.filename):
        return True
    
    return False


# ========== SPA 前端入口 ==========
@app.route('/')
def index():
    """返回 SPA 前端页面"""
    # 直接读取并返回 HTML 文件内容
    html_path = os.path.join(STATIC_DIR, 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    return '<h1>Frontend not found</h1><p>Build the frontend first.</p>', 404


# ========== API 接口 ==========
@app.route('/api/files', methods=['GET'])
def api_get_files():
    """获取已上传的文件列表"""
    try:
        files = container.get_document_processor().get_uploaded_files()
        # 附带文件信息（大小、类型等）
        file_info = []
        for f in files:
            fp = os.path.join(UPLOAD_FOLDER, f)
            stat = os.stat(fp) if os.path.exists(fp) else None
            file_info.append({
                'name': f,
                'size': stat.st_size if stat else 0,
                'mtime': stat.st_mtime if stat else 0
            })
        return api_response(0, '', file_info)
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        return api_response(-1, str(e))


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """上传文档"""
    # 检查是否有文件
    if 'file' not in request.files:
        return api_response(-1, '没有选择文件')

    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return api_response(-1, '没有选择文件')

    # 检查文件扩展名
    if not file or not allowed_file(file.filename):
        return api_response(-1, f'不支持的文件格式，允许：{ALLOWED_EXTENSIONS}')

    # 检查文件大小
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        return api_response(-1, f'文件大小超过限制，最大允许 {max_size_mb:.0f}MB')

    # 验证 MIME 类型
    if not validate_mime_type(file):
        return api_response(-1, '文件类型验证失败，请确保上传的是合法文件')

    try:
        original_filename = file.filename
        # 保留原始文件名，仅过滤危险字符
        filename = original_filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        
        # 处理重名文件
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            filename = f"{base}_{counter}{ext}"
            counter += 1

        # 验证路径安全性（防止路径遍历攻击）
        if not is_safe_path(UPLOAD_FOLDER, filename):
            return api_response(-1, '非法文件路径')

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # 保存文件（处理具体异常）
        try:
            file.save(file_path)
        except PermissionError as e:
            logger.error(f"文件保存权限不足: {str(e)}")
            return api_response(-1, '保存文件失败，权限不足')
        except IOError as e:
            logger.error(f"保存文件失败: {str(e)}")
            return api_response(-1, f'保存文件失败: {str(e)}')

        # 创建索引
        index = container.get_vector_store().load_from_documents(file_path=file_path)
        if index:
            container.get_query_engine().create_query_engine(index)
            return api_response(0, f'"{filename}" 上传并建索引成功', {'filename': filename})
        else:
            # 尝试重建全部索引
            index = container.get_vector_store().load_from_documents(input_dir=UPLOAD_FOLDER)
            if index:
                container.get_query_engine().create_query_engine(index)
                return api_response(0, f'"{filename}" 上传成功，已重建索引', {'filename': filename})
            else:
                return api_response(-1, '文件上传成功但索引创建失败')
    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        return api_response(-1, f'参数错误: {str(e)}')
    except Exception as e:
        logger.error(f"上传文件时发生未知错误: {str(e)}")
        return api_response(-1, f'操作失败: {str(e)}')


@app.route('/api/delete/<filename>', methods=['DELETE'])
def api_delete_file(filename):
    """删除文件"""
    try:
        # 仅过滤危险字符，保留中文
        safe_name = filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        
        # 验证路径安全性（防止路径遍历攻击）
        if not is_safe_path(UPLOAD_FOLDER, safe_name):
            return api_response(-1, '非法文件路径')
        
        try:
            if container.get_document_processor().delete_file(safe_name):
                index = container.get_vector_store().load_from_documents(input_dir=UPLOAD_FOLDER)
                if index:
                    container.get_query_engine().create_query_engine(index)
                return api_response(0, f'"{safe_name}" 删除成功')
            else:
                return api_response(-1, f'删除 "{safe_name}" 失败，文件可能不存在')
        except FileNotFoundError as e:
            logger.error(f"文件不存在: {str(e)}")
            return api_response(-1, f'文件 "{safe_name}" 不存在')
        except PermissionError as e:
            logger.error(f"删除文件权限不足: {str(e)}")
            return api_response(-1, f'删除文件失败，权限不足')
        except OSError as e:
            logger.error(f"删除文件时发生系统错误: {str(e)}")
            return api_response(-1, f'删除文件失败: {str(e)}')
    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        return api_response(-1, f'参数错误: {str(e)}')
    except Exception as e:
        logger.error(f"删除文件时发生未知错误: {str(e)}")
        return api_response(-1, str(e))


# 问题最大长度限制
MAX_QUESTION_LENGTH = 2000

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """智能问答"""
    try:
        # 检查请求内容类型
        if not request.is_json:
            return api_response(-1, '请求格式错误，需要 JSON 格式')
        
        data = request.get_json()
        if data is None:
            return api_response(-1, '请求体为空')
        
        # 验证问题参数是否存在
        if 'question' not in data:
            return api_response(-1, '缺少 question 参数')
        
        question = data.get('question', '').strip()

        # 验证问题非空
        if not question:
            return api_response(-1, '问题不能为空')
        
        # 验证问题长度
        if len(question) > MAX_QUESTION_LENGTH:
            return api_response(-1, f'问题长度超过限制（最大 {MAX_QUESTION_LENGTH} 字符）')

        answer = container.get_query_engine().query(question)
        return api_response(0, '', {'question': question, 'answer': answer})
    except ConnectionError as e:
        logger.error(f"连接错误: {str(e)}")
        return api_response(-1, '服务暂时不可用，请稍后重试')
    except TimeoutError as e:
        logger.error(f"请求超时: {str(e)}")
        return api_response(-1, '请求超时，请重试')
    except ValueError as e:
        logger.error(f"参数验证失败: {str(e)}")
        return api_response(-1, f'参数错误: {str(e)}')
    except Exception as e:
        logger.error(f"查询时发生未知错误: {str(e)}")
        return api_response(-1, f'查询出错: {str(e)}')


@app.route('/api/status', methods=['GET'])
def api_status():
    """获取系统状态"""
    try:
        files = container.get_document_processor().get_uploaded_files()
        engine_ready = container.get_query_engine().query_engine is not None
        return api_response(0, '', {
            'file_count': len(files),
            'engine_ready': engine_ready,
            'model_type': MODEL_TYPE
        })
    except OSError as e:
        logger.error(f"读取文件列表失败: {str(e)}")
        return api_response(-1, '获取状态失败')
    except Exception as e:
        logger.error(f"获取状态时发生未知错误: {str(e)}")
        return api_response(-1, str(e))
