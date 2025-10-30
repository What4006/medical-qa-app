# backend/app/schemas/department_schema.py
from ..core.extensions import ma
from marshmallow import fields
from datetime import datetime # 需要 datetime 用于模拟 ID
import random # 引入 random 用于模拟 ID

class DepartmentSchema(ma.Schema):
    # 根据文档 API#15 的响应格式 
    # 使用 Method 字段动态生成符合 'dept-xxx' 格式的 ID
    # 注意：这种模拟 ID 的方式不保证全局唯一，仅用于演示
    # 推荐使用数据库自增 ID (fields.Int(attribute="id"))
    id = fields.Method("generate_dept_id")
    name = fields.Str(required=True)
    description = fields.Str()

    # 用于生成模拟 dept-xxx ID 的方法
    def generate_dept_id(self, obj):
        # obj 是 DepartmentModel 实例
        # 使用数据库的真实 ID 结合随机数生成一个模拟 ID
        timestamp_hash = hash(datetime.now().timestamp() + random.random())
        return f"dept-{obj.id}-{abs(timestamp_hash) % 1000}" # 结合真实 ID 增加唯一性

    class Meta:
        # 指定序列化时包含的字段
        fields = ("id", "name", "description")
        ordered = True # 保持字段输出顺序与定义一致