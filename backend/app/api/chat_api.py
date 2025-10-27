from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services import llm_service
from ..services.history_service import get_chat_history, find_or_create_main_ai_consultation, add_chat_message_to_consultation, start_new_chat_session, generate_medical_record_from_history

# 创建 'chat_bp' 蓝图
chat_bp = Blueprint('chat_api', __name__, url_prefix='/api/chat')

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