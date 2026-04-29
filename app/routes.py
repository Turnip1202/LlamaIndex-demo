# 路由文件 - RESTful API 后端

from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from app import app
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.services.query_engine import QueryEngine
import os
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from werkzeug.utils import secure_filename
import uuid

# 获取项目根目录（app/ 的上级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# 全局变量
vector_store = VectorStore()
query_engine = QueryEngine()
document_processor = DocumentProcessor()

# 尝试加载现有文档并创建索引
def init_index(upload_dir):
    try:
        if os.path.exists(upload_dir) and len(os.listdir(upload_dir)) > 0:
            print("初始化索引...")
            index = vector_store.load_from_documents(input_dir=upload_dir)
            if index:
                query_engine.create_query_engine(index)
                print("索引初始化成功")
            else:
                print("索引初始化失败")
        else:
            print("上传目录为空，跳过索引初始化")
    except Exception as e:
        print(f"初始化索引时出错: {str(e)}")

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        files = document_processor.get_uploaded_files()
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
        return jsonify({'code': 0, 'data': file_info})
    except Exception as e:
        return jsonify({'code': -1, 'msg': str(e)})


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """上传文档"""
    if 'file' not in request.files:
        return jsonify({'code': -1, 'msg': '没有选择文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': -1, 'msg': '没有选择文件'})

    if not file or not allowed_file(file.filename):
        return jsonify({'code': -1, 'msg': f'不支持的文件格式，允许：{ALLOWED_EXTENSIONS}'})

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

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # 创建索引
        index = vector_store.load_from_documents(file_path=file_path)
        if index:
            query_engine.create_query_engine(index)
            return jsonify({
                'code': 0,
                'msg': f'"{filename}" 上传并建索引成功',
                'data': {'filename': filename}
            })
        else:
            # 尝试重建全部索引
            index = vector_store.load_from_documents(input_dir=UPLOAD_FOLDER)
            if index:
                query_engine.create_query_engine(index)
                return jsonify({'code': 0, 'msg': f'"{filename}" 上传成功，已重建索引', 'data': {'filename': filename}})
            else:
                return jsonify({'code': -1, 'msg': '文件上传成功但索引创建失败'})
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'操作失败: {str(e)}'})


@app.route('/api/delete/<filename>', methods=['DELETE'])
def api_delete_file(filename):
    """删除文件"""
    try:
        # 仅过滤危险字符，保留中文
        safe_name = filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        if document_processor.delete_file(safe_name):
            index = vector_store.load_from_documents(input_dir=UPLOAD_FOLDER)
            if index:
                query_engine.create_query_engine(index)
            return jsonify({'code': 0, 'msg': f'"{safe_name}" 删除成功'})
        else:
            return jsonify({'code': -1, 'msg': f'删除 "{safe_name}" 失败，文件可能不存在'})
    except Exception as e:
        return jsonify({'code': -1, 'msg': str(e)})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """智能问答"""
    try:
        data = request.get_json() or request.form
        question = data.get('question', '').strip()

        if not question:
            return jsonify({'code': -1, 'msg': '问题不能为空'})

        answer = query_engine.query(question)
        return jsonify({
            'code': 0,
            'data': {
                'question': question,
                'answer': answer
            }
        })
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'查询出错: {str(e)}'})


@app.route('/api/status', methods=['GET'])
def api_status():
    """获取系统状态"""
    try:
        files = document_processor.get_uploaded_files()
        engine_ready = query_engine.query_engine is not None
        return jsonify({
            'code': 0,
            'data': {
                'file_count': len(files),
                'engine_ready': engine_ready,
                'model_type': 'hybrid'
            }
        })
    except Exception as e:
        return jsonify({'code': -1, 'msg': str(e)})
