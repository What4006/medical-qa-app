# backend/app/schemas/appointment_schema.py
from ..core.extensions import ma
from marshmallow import fields, validate

class AppointmentRequestSchema(ma.Schema):
    """
    用于验证创建预约请求 (POST /api/appointments) 的 Schema
    [cite: 1030]
    """
    doctorId = fields.Int(required=True)
    appointmentDate = fields.Date(required=True, format="%Y-%m-%d")
    appointmentTime = fields.Str(required=True, validate=validate.Length(min=2)) # e.g., "上午"
    medicalRecordId = fields.Int(required=False)

class AppointmentResponseSchema(ma.Schema):
    """
    用于序列化返回的预约信息
    [cite: 1044]
    """
    id = fields.Int()
    doctorId = fields.Int(attribute="doctor_id")
    
    # 嵌套获取医生的姓名 [cite: 1049]
    doctorName = fields.Str(attribute="doctor.user.full_name") 
    
    # 将 appointment_time (DateTime) 拆分为日期和时段
    appointmentDate = fields.Date(attribute="appointment_time")
    appointmentTime = fields.Method("get_appointment_time_slot")
    
    status = fields.Str()
    createdAt = fields.DateTime(attribute="created_at")

    def get_appointment_time_slot(self, obj):
        # 根据时间戳返回 "上午" 或 "下午" [cite: 1051]
        if obj.appointment_time:
            return "上午" if obj.appointment_time.hour < 12 else "下午"
        return "未知"