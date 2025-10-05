from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services import llm_service
from ..services.history_service import get_chat_history, find_or_create_main_ai_consultation, add_chat_message_to_consultation

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
    【升级版】获取当前用户的完整AI对话历史。
    它会自动查找或创建用户的唯一会话。
    """
    try:
        user_id = get_jwt_identity()

        # 1. 智能查找或创建用户的主问诊记录
        main_consultation = find_or_create_main_ai_consultation(user_id)
        
        # 2. 获取这个唯一的问诊ID
        consultation_id = main_consultation.id
        
        # 3. 使用这个ID获取所有相关的聊天记录
        history = get_chat_history(user_id, consultation_id)
        
        # 4. 将ID和历史记录一起返回给前端
        #    前端需要这个ID来进行后续的“继续对话”操作
        return jsonify({
            "consultation_id": consultation_id,
            "history": history
        }), 200

    except Exception as e:
        print(f"Error in /api/chat/history: {e}")
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500
    
@chat_bp.route('/continue', methods=['POST'])
@jwt_required()
def continue_chat():
    """在已存在的问诊中继续对话"""
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.json
    consultation_id = data.get('consultation_id')
    question = data.get('question')

    if not consultation_id or not question:
        return jsonify({"msg": "Missing consultation_id or question parameter"}), 400

    try:
        user_id = get_jwt_identity()

        # 1. 调用(模拟的)LLM服务获取AI的回答
        ai_answer = llm_service.get_ai_response(question)

        # 2. 调用service函数，将新的问答对追加到数据库
        result = add_chat_message_to_consultation(user_id, consultation_id, question, ai_answer)

        # 3. 检查service的返回结果
        if result is None:
            # 如果service返回None，说明问诊ID无效或用户权限不足
            return jsonify({"msg": "Invalid consultation_id or permission denied"}), 404
        
        # 4. 成功后，只将AI的回答返回给前端
        return jsonify({"answer": ai_answer}), 200

    except Exception as e:
        print(f"Error in /api/chat/continue: {e}")
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500