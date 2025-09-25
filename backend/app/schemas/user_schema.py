#9.23——用于实现获取当前用户信息的API--w4006
from ..core.extensions import ma
from marshmallow import fields

class UserSchema(ma.Schema):
    nickname = fields.Str(attribute="full_name")
    gender = fields.Str()
    age = fields.Int()
    class Meta:
        fields = ("nickname", "gender", "age")