from ..core.extensions import ma
from marshmallow import fields, validate

# 登录请求的数据校验 Schema
class LoginSchema(ma.Schema):
    # 文档要求字段为 phone, 但模型中使用 username 存储手机号
    username = fields.Str(required=True, validate=validate.Length(min=11, max=11), data_key="phone")
    password = fields.Str(required=True, validate=validate.Length(min=6, max=18))
    # user_type 用于业务逻辑判断，1=patient, 2=doctor
    user_type = fields.Int(required=True, validate=validate.OneOf([1, 2]))

# 患者注册请求的数据校验 Schema
class PatientRegisterSchema(ma.Schema):
    username = fields.Str(required=True, validate=validate.Length(min=11, max=11), data_key="phone")
    password = fields.Str(required=True, validate=validate.Length(min=6, max=18))
    full_name = fields.Str(required=True) # 假设前端会传来 full_name
    birth_date = fields.Date(required=True)

# 医生注册请求的数据校验 Schema
class DoctorRegisterSchema(ma.Schema):
    # 字段名与文档中的 form-data 字段名保持一致
    phone = fields.Str(required=True, validate=validate.Length(equal=11))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=18))
    license_id = fields.Str(required=True, validate=validate.Length(equal=15))
    hospital = fields.Str(required=True)
    department = fields.Str(required=True)
    title = fields.Str(required=True)
    # full_name 是我们模型需要的，前端也应该提供
    full_name = fields.Str(required=True)
    
    # 'certificate' 文件字段将会在 API 视图中单独处理，不在这里校验

# 用于 /api/auth/me 返回的当前用户详细信息 Schema
# 为了区分不同角色的信息，我们定义嵌套的 Schema
class PatientInfoSchema(ma.Schema):
    real_name = fields.Str(attribute="full_name")
    birth_date = fields.Date()
    age = fields.Int() # Marshmallow 会自动调用 user.age 属性

class DoctorInfoSchema(ma.Schema):
    real_name = fields.Str(attribute="full_name")
    hospital = fields.Str() # 假设医院信息在 bio 或其他字段
    department = fields.Str(attribute="specialty")
    # audit_status 暂时硬编码或从数据库特定字段获取
    audit_status = fields.Int(dump_default=1)

class UserDetailSchema(ma.Schema):
    id = fields.Int()
    phone = fields.Str(attribute="username")
    user_type = fields.Method("get_user_type")
    status = fields.Int(dump_default=1)
    
    patient_info = fields.Method("get_patient_info")
    doctor_info = fields.Nested(DoctorInfoSchema, attribute="doctor_info")

    def get_user_type(self, obj):
        return 1 if obj.role == 'patient' else 2

    # --- 核心修改：用手动构建字典的方式重写这个方法 ---
    def get_patient_info(self, obj):
        """
        手动构建 patient_info 字典。
        这种方法最直接，可以避免因版本问题导致的嵌套序列化失败。
        """
        if obj.role == 'patient':
            return {
                'real_name': obj.full_name,
                # .isoformat() 确保日期能被正确转换为 "YYYY-MM-DD" 格式的字符串
                'birth_date': obj.birth_date.isoformat() if obj.birth_date else None,
                'age': obj.age
            }
        return None