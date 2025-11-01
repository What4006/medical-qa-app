# backend/app/api/doctor_api.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..services import doctor_service
from ..schemas.doctor_schema import DoctorListSchema
import logging

# [cite: 1602]
doctor_bp = Blueprint('doctor_api', __name__, url_prefix='/api/doctors')

@doctor_bp.route('', methods=['GET']) # [cite: 1601]
@jwt_required() # [cite: 1607-1609]
def get_doctor_list():
    """
    API #16: 获取医生列表
    
    """
    try:
        # 1. 获取科室筛选参数
        # [cite: 1606]
        # 我们假设前端传递的是 DepartmentModel 的整数ID
        department_id = request.args.get('departmentId', type=int)
        
        # 2. 调用服务层获取医生数据
        doctors = doctor_service.get_doctors(department_id)
        
        # 3. 序列化数据
        # [cite: 1612]
        schema = DoctorListSchema(many=True)
        result = schema.dump(doctors)
        
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Error in /api/doctors GET: {e}", exc_info=True)
        # [cite: 1630-1633]
        return jsonify({"error_code": 500, "message": "获取医生列表失败"}), 500