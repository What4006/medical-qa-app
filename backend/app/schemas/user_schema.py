#9.23——用于实现获取当前用户信息的API--w4006
from ..core.extensions import ma

class UserSchema(ma.Schema):
    class Meta:
        fields=("nickname","gender","age")