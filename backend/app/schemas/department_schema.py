# backend/app/schemas/department_schema.py
from ..core.extensions import ma
from marshmallow import fields
from datetime import datetime # 需要 datetime 用于模拟 ID
import random # 引入 random 用于模拟 ID

class DepartmentSchema(ma.Schema):
    
    id = fields.Int(attribute="id")
    name = fields.Str(required=True)
    description = fields.Str()

    class Meta:
        # 指定序列化时包含的字段
        fields = ("id", "name", "description")
        ordered = True # 保持字段输出顺序与定义一致