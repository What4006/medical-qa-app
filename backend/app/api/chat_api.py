import os
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

# 导入现有的服务
from ..services import llm_service
from ..services.history_service import (
    get_chat_history, 
    find_or_create_main_ai_consultation, 
    add_chat_message_to_consultation, 
    start_new_chat_session, 
    generate_medical_record_from_history
)

# 创建 'chat_bp' 蓝图
chat_bp = Blueprint('chat_api', __name__, url_prefix='/api/chat')

# --- 新增：文件上传配置 ---
# (参考 patient_ai.html 的 accept 属性，允许图片、pdf、office文档等)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# --------------------------

#这个是按照分对话块的方式写的
"""
@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history_records():
    try:
        user_id = get_jwt_identity()
        # 前端需要通过URL查询参数 ?consultation_id=xxx 来指定要看哪次问诊
        consultation_id = request.args.get('consultation_id', type=int)

        if not consultation_id:
            return jsonify({"msg": "Missing consultation_id parameter"}), 400

        # 调用 service 函数获取处理好的数据
        history = get_chat_history(user_id, consultation_id)
        
        return jsonify(history), 200
        
    except Exception as e:
        print(f"Error in /api/chat/history: {e}")
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500
"""
#这个是按照显示所有历史内容来写的
@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history_records():
    """
    获取当前用户所有的AI对话历史记录。
    """
    try:
        user_id = get_jwt_identity()

        # 1. 调用新的service函数，获取全部历史记录
        history = get_chat_history(user_id)
        
        # 2. 为了兼容前端的“继续对话”功能，我们仍然需要一个默认的consultation_id。
        #    这里我们查找用户最新的一个会话ID。
        latest_consultation = find_or_create_main_ai_consultation(user_id) # 复用此函数查找或创建
        
        # 3. 返回所有历史记录和最新会话的ID
        return jsonify({
            "consultation_id": latest_consultation.id,
            "history": history
        }), 200

    except Exception as e:
        print(f"Error in /api/chat/history: {e}")
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500
    
@chat_bp.route('/medical', methods=['POST']) # 1. 路由从 /continue 修改为 /medical
@jwt_required()
def chat_medical(): # 2. 函数名修改
    """
    在最新的问诊中继续对话。
    这个接口会智能查找最新的会话ID并追加消息。
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"msg": "Missing question parameter"}), 400

    try:
        user_id = get_jwt_identity()
        
        # 3. 不再从前端获取ID，而是从后端智能查找最新的会话(这里似乎前端也没有传回id只能自己查找了)
        latest_consultation = find_or_create_main_ai_consultation(user_id)
        consultation_id = latest_consultation.id

        # 4. 后续逻辑保持不变：获取AI回答并存入数据库
        ai_answer = llm_service.get_ai_response(question)
        add_chat_message_to_consultation(user_id, consultation_id, question, ai_answer)
        
        return jsonify({"answer": ai_answer}), 200

    except Exception as e:
        print(f"Error in /api/chat/medical: {e}")
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500

# --- 新增：API #11 ---
# 路由：POST /api/chat/medical/upload (带文件的问答)
@chat_bp.route('/medical/upload', methods=['POST'])
@jwt_required()
def chat_medical_upload():
    """
    发送医疗问题和文件到 AI 模型。
    
    """
    try:
        user_id = get_jwt_identity()
        
        # 1. 从 FormData 获取文本和文件 [cite: 1545]
        question = request.form.get('question')
        files = request.files.getlist('files')

        if not question:
            return jsonify({"error_code": 400, "message": "未提供问题文本"}), 400
        if not files or len(files) == 0:
            return jsonify({"error_code": 400, "message": "未提供文件"}), 400

        file_urls = []
        
        # 2. 定义文件保存路径 (例如: backend/uploads/chat_files/)
        upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'chat_files')
        os.makedirs(upload_folder, exist_ok=True)

        # 3. 遍历和保存文件
        for file in files:
            if file and allowed_file(file.filename):
                # 生成安全且唯一的文件名
                filename = secure_filename(f"{user_id}_{datetime.utcnow().timestamp():.0f}_{file.filename}")
                file_path_on_disk = os.path.join(upload_folder, filename)
                
                # 保存文件到服务器
                file.save(file_path_on_disk)
                
                # 数据库中保存相对路径
                db_file_path = os.path.join('uploads', 'chat_files', filename).replace('\\', '/')
                
                # 生成可供AI访问的公网URL
                # (依赖于 app/__init__.py 中的 @app.route('/uploads/<path:filename>'))
                public_url = f"{request.host_url}{db_file_path}"
                file_urls.append(public_url)
            else:
                logging.warning(f"Skipped disallowed file: {file.filename}")

        # 4. 组合问题文本和文件URL
        if not file_urls:
            return jsonify({"error_code": 400, "message": "上传的文件均不合法"}), 400
            
        file_links_str = "\n".join(file_urls)
        combined_question = f"{question}\n\n附件文件 (Accessible URLs):\n{file_links_str}"
        
        logging.info(f"Combined question for LLM: {combined_question}")

        # 5. 调用 LLM 服务 (使用合并后的文本)
        ai_answer = llm_service.get_ai_response(combined_question)
        
        # 6. 保存到历史记录 (保存合并后的问题)
        latest_consultation = find_or_create_main_ai_consultation(user_id)
        add_chat_message_to_consultation(user_id, latest_consultation.id, combined_question, ai_answer)
        
        # 7. 返回成功响应 [cite: 1553]
        return jsonify({"answer": ai_answer}), 200

    except Exception as e:
        logging.error(f"Error in /api/chat/medical/upload: {e}", exc_info=True)
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500 [cite: 1563]
# --- API #11 结束 ---

@chat_bp.route('/new', methods=['POST'])
@jwt_required()
def new_chat():
    """通知后端开启新对话"""
    try:
        user_id = get_jwt_identity()
        # 调用-service层来处理开启新会话的逻辑
        new_chat_id = start_new_chat_session(user_id)
        return jsonify({
        "success": True,
        "message": "新对话已创建",
        "chatId": new_chat_id
    }), 200
    except Exception as e:
        print(f"Error in /api/chat/new: {e}")
    return jsonify({"error_code": 500, "message": "服务器内部错误，无法创建新对话"}), 500

@chat_bp.route('/medical/record', methods=['POST'])
@jwt_required()
def generate_medical_record():
    """根据用户的问诊历史记录生成结构化电子病历"""
    try:
        user_id = get_jwt_identity()
        # 调用service层生成病历
        medical_record = generate_medical_record_from_history(user_id)
        if not medical_record:
            return jsonify({"error_code": 404, "message": "无足够的问诊记录生成病历"}), 404
        return jsonify(medical_record), 200
    except Exception as e:
        print(f"Error in /api/chat/medical/record: {e}")
    return jsonify({"error_code": 500, "message": "生成病历失败，请稍后重试"}), 500