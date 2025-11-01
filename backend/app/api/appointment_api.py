from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from ..services import appointment_service
from ..schemas.appointment_schema import AppointmentRequestSchema, AppointmentResponseSchema
import logging

# 创建蓝图，定义 API 路由前缀
appointment_bp = Blueprint('appointment_api', __name__, url_prefix='/api/appointments')

@appointment_bp.route('', methods=['POST'])
@jwt_required()
def create_appointment():
    """
    API #16: 创建医生预约
    [cite: 1023-1027]
    """
    try:
        # 1. 获取并校验请求数据
        # [cite: 1029-1030]
        data = AppointmentRequestSchema().load(request.json)
        
        # 2. 获取当前登录的患者ID
        patient_user_id = get_jwt_identity()

        # 3. 调用服务层处理业务逻辑
        appointment, error_msg = appointment_service.create_appointment(data, patient_user_id)

        # 4. 根据服务层返回结果，响应
        if not appointment:
            # 根据文档，404 "医生不存在" [cite: 1063] 或 400 "不可预约" [cite: 1058]
            error_code = 404 if "不存在" in error_msg else 400
            return jsonify({"error_code": error_code, "message": error_msg}), error_code

        # 5. 序列化并返回成功响应
        # [cite: 1044-1054]
        response_data = AppointmentResponseSchema().dump(appointment)
        return jsonify(response_data), 200

    except ValidationError as err:
        logging.warning(f"预约数据校验失败: {err.messages}")
        return jsonify({"error_code": 400, "message": err.messages}), 400
    except Exception as e:
        logging.error(f"创建预约时发生意外错误: {e}", exc_info=True)
        return jsonify({"error_code": 500, "message": "服务器内部错误"}), 500