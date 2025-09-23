#9.23——用于实现获取当前用户信息的API--w4006
from ..models.user_model import UserModel 

def get_user_by_id(user_id):
    #在数据库里查找用户
    user=UserModel.query.get(user_id)
    return user