from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.history_service import get_recent_consultation
# 导入需要检查类型的模型
from ..models.consultation_model import AIConsultationModel, DoctorConsultationModel

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