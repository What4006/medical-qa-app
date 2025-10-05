from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.history_service import get_recent_consultation, get_all_consulations
# 导入需要检查类型的模型
from ..models.consultation_model import AIConsultationModel, DoctorConsultationModel
from ..services.history_service import create_ai_consultation_record
history_bp = Blueprint('history_api', __name__, url_prefix='/api/history')

@history_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_history():
    # 实例化 schemas
    from ..schemas.history_schema import AiConsultationSchema, DoctorConsultationSchema
    ai_schema = AiConsultationSchema()
    doctor_schema = DoctorConsultationSchema()

    current_user_id = get_jwt_identity()
    # 调用更新后的 Service 函数，它会返回一个混合类型的对象或 None
    record = get_recent_consultation(current_user_id)
    
    if not record:
        return jsonify(None), 200
        
    # 使用 isinstance() 来判断 record 对象的具体类型
    if isinstance(record, AIConsultationModel):
        # 如果是 AI 问诊记录，使用 AiConsultationSchema
        return jsonify(ai_schema.dump(record)), 200
    elif isinstance(record, DoctorConsultationModel):
        # 如果是医生问诊记录，使用 DoctorConsultationSchema
        return jsonify(doctor_schema.dump(record)), 200
    else:
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500
    
@history_bp.route('/all',methods=['GET'])
@jwt_required()
def get_all_history():
    from ..schemas.history_schema import AiConsultationSchema, DoctorConsultationSchema
    ai_schema = AiConsultationSchema(many=True)
    doctor_schema = DoctorConsultationSchema(many=True)

    current_user_id = get_jwt_identity()
    ai_records,doctor_records=get_all_consulations(current_user_id)
    ai_list = ai_schema.dump(ai_records)
    doctor_list = doctor_schema.dump(doctor_records)
    all_records=ai_list+doctor_list

    sorted_records=sorted(all_records,key=lambda r: (r.get('date',''),r.get('time','')),reverse=True)
    return jsonify(sorted_records),200

# 将 /api/history/create 路由添加到现有的 history_bp 蓝图中
@history_bp.route('/create', methods=['POST'])
@jwt_required()
def create_history_record():
    """保存用户与 AI 的问诊对话记录到数据库"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        question = data.get('question')
        answer = data.get('answer')

        if not question or not answer:
            return jsonify({"msg": "Missing question or answer"}), 400

        # 调用 service 函数执行数据库操作
        new_record = create_ai_consultation_record(user_id, question, answer)
        
        # 按照文档格式返回响应
        return jsonify({
            "id": str(new_record.id),  # 将数字ID转为字符串以匹配文档
            "question": question,
            "answer": answer,
            "createdAt": new_record.created_at.isoformat() + "Z"
        }), 200
    
    except Exception as e:
        print(f"Error in /api/history/create: {e}")
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500