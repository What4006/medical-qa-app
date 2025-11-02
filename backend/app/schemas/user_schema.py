#9.23——用于实现获取当前用户信息的API--w4006
from ..core.extensions import ma
from marshmallow import fields, validate, Schema

class UserSchema(ma.Schema):
    nickname = fields.Str(attribute="full_name")
    gender = fields.Str()
    age = fields.Int()
    class Meta:
        fields = ("nickname", "gender", "age")

class ChangePasswordRequestSchema(Schema):
    """用于 API #23: 修改密码 请求数据校验"""
    oldPassword = fields.Str(required=True, data_key="oldPassword")
    # 长度校验满足文档要求 (>=8 位)
    newPassword = fields.Str(required=True, data_key="newPassword", 
                             validate=[validate.Length(min=8)]) 

class UpdateUserInfoRequestSchema(Schema):
    """用于 API #22: 更新用户信息 请求数据校验 [cite: 1059]"""
    fullname = fields.Str(required=True)
    gender = fields.Str(required=True, validate=validate.OneOf(["male", "female"]))
    # 必须是 YYYY-MM-DD 格式
    birthday = fields.Date(required=True, format="%Y-%m-%d")
    phone = fields.Str(required=True, validate=validate.Length(equal=11))
    idCard = fields.Str(required=True, validate=validate.Length(equal=18))
    insuranceCard = fields.Str(required=False, allow_none=True)
    email = fields.Email(required=True)
    
    # [cite_start]病史信息 (对应 API 文档 [cite: 1059] 的字段)
    pastHistory = fields.Str(required=False, allow_none=True) 
    personalHistory = fields.Str(required=False, allow_none=True)
    familyHistory = fields.Str(required=False, allow_none=True)