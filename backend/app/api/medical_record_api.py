# backend/app/api/medical_record_api.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services import medical_record_service
from ..schemas.medical_record_schema import MedicalRecordListSchema, MedicalRecordDetailSchema
import logging

# 创建蓝图，定义 API 路由前缀
medical_record_bp = Blueprint('medical_record_api', __name__, url_prefix='/api/medical-records')

@medical_record_bp.route('', methods=['GET'])
@jwt_required()
def get_medical_record_list():
    """
    API #18: 获取病历记录列表
    
    """
    try:
        patient_user_id = get_jwt_identity()
        
        # 1. 调用服务层获取数据
        records = medical_record_service.get_records_for_patient(patient_user_id)
        
        # 2. 序列化列表
        # [cite: 1641-1642]
        schema = MedicalRecordListSchema(many=True)
        result = schema.dump(records)
        
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in /api/medical-records GET list: {e}", exc_info=True)
        # [cite: 1658-1662]
        return jsonify({"error_code": 500, "message": "服务器内部错误，获取病历记录失败"}), 500

@medical_record_bp.route('/<int:recordId>', methods=['GET']) #
@jwt_required()
def get_medical_record_detail(recordId):
    """
    API #19: 获取病历详情
    
    """
    try:
        patient_user_id = get_jwt_identity()
        
        # 1. 调用服务层获取特定记录，服务层会处理权限（确保病历属于该用户）
        record = medical_record_service.get_record_detail(patient_user_id, recordId)

        if not record:
            # [cite: 1695-1698]
            return jsonify({"error_code": 404, "message": f"未找到ID为{recordId}的病历记录"}), 404

        # 2. 序列化详情
        # [cite: 1680-1682]
        schema = MedicalRecordDetailSchema()
        result = schema.dump(record)
        
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in /api/medical-records/{recordId} GET detail: {e}", exc_info=True)
        # [cite: 1703-1706]
        return jsonify({"error_code": 500, "message": "服务器内部错误，获取病历详情失败"}), 500