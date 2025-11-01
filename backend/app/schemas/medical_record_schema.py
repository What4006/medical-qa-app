# backend/app/schemas/medical_record_schema.py
from ..core.extensions import ma
from marshmallow import fields

class MedicalRecordListSchema(ma.Schema):
    """
    序列化病历列表 (API #18)
    使用中文键名 [cite: 1642]
    """
    # [cite: 1642]
    id = fields.Str(attribute="id") # 文档要求 String
    #
    主诉 = fields.Str(attribute="chief_complaint")
    #
    诊断 = fields.Str(attribute="diagnosis")
    #
    createdAt = fields.DateTime(attribute="created_at")

class MedicalRecordDetailSchema(ma.Schema):
    """
    序列化病历详情 (API #19)
    使用中文键名 [cite: 1682]
    """
    # [cite: 1682]
    id = fields.Str(attribute="id") # 文档要求 String
    #
    主诉 = fields.Str(attribute="chief_complaint")
    #
    现病史 = fields.Str(attribute="history_present_illness")
    #
    既往史 = fields.Str(attribute="past_medical_history")
    #
    个人史 = fields.Str(attribute="personal_history")
    #
    家族史 = fields.Str(attribute="family_history")
    #
    诊断 = fields.Str(attribute="diagnosis")
    #
    createdAt = fields.DateTime(attribute="created_at")