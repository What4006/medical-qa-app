# backend/app/schemas/doctor_schema.py
from ..core.extensions import ma
from marshmallow import fields

class DoctorListSchema(ma.Schema):
    """
    序列化医生列表，严格按照 API #16 文档格式
   
    """
    
    # --- 直接/间接来自 Model ---
    id = fields.Int(attribute="id") #
    name = fields.Str(attribute="user.full_name") #
    title = fields.Str() #
    departmentName = fields.Str(attribute="specialty") #
    introduction = fields.Str(attribute="bio") #

    # --- 需计算或假设的字段 ---
    
    # specialty (文档要求为数组)
    specialty = fields.Method("get_specialty_array") #
    
    # available & availableDays (来自 available_slots)
    available = fields.Method("get_is_available") #
    availableDays = fields.Method("get_available_days") #

    # --- 数据库模型中没有，但文档中要求的字段 (提供默认值) ---
    avatar = fields.Str(dump_default="https://example.com/avatar.jpg") #

    def get_specialty_array(self, obj):
        """
        (已修正)
        读取 DoctorModel.specialty 字符串，
        并将其作为数组返回，以满足 API #16 的格式要求。
        """
        if obj.specialty:
            # 例如： obj.specialty 是 "心内科"
            # 返回 ["心内科"]
            return [obj.specialty]
        return ["暂未填写"]

    def get_is_available(self, obj):
        """
        检查 `available_slots` JSON 字段中 是否有 "availableDays"
        """
        if obj.available_slots and obj.available_slots.get("availableDays"):
            return len(obj.available_slots.get("availableDays")) > 0
        return False

    def get_available_days(self, obj):
        """
        直接返回 `available_slots` JSON 字段中 的列表
        """
        if obj.available_slots:
            return obj.available_slots.get("availableDays", [])
        return []