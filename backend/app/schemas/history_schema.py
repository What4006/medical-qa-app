from ..core.extensions import ma
from marshmallow import fields

# 1. AI 问诊记录的 Schema
class AiConsultationSchema(ma.Schema):
    id = fields.Int()
    type = fields.Constant("ai")
    title = fields.Str(attribute="ai_diagnosis")
    status = fields.Str()
    summary = fields.Str(attribute="ai_analysis")

    # 使用 Method 字段从同一个 created_at 派生出 date 和 time
    date = fields.Method("get_creation_date")
    time = fields.Method("get_creation_time")

    # 自定义方法，用于生成 date 字段的值
    def get_creation_date(self, obj):
        # obj 是传入的 AIConsultationModel 实例
        if not obj.created_at:
            return None
        return obj.created_at.strftime("%Y-%m-%d")

    # 自定义方法，用于生成 time 字段的值
    def get_creation_time(self, obj):
        if not obj.created_at:
            return None
        return obj.created_at.strftime("%H:%M")


# 2. 医生问诊记录的 Schema
class DoctorConsultationSchema(ma.Schema):
    id = fields.Int()
    type = fields.Constant("doctor")
    title = fields.Str(attribute="patient_symptoms") 
    status = fields.Str()
    summary = fields.Str(attribute="doctor_diagnosis")
    department = fields.Str()
    doctor = fields.Str(attribute="doctor.full_name")

    # 对 appointment_time 使用同样的方法
    date = fields.Method("get_appointment_date")
    time = fields.Method("get_appointment_time")

    def get_appointment_date(self, obj):
        if not obj.appointment_time:
            return None
        return obj.appointment_time.strftime("%Y-%m-%d")

    def get_appointment_time(self, obj):
        if not obj.appointment_time:
            return None
        return obj.appointment_time.strftime("%H:%M")