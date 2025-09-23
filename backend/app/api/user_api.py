from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..services.user_service import get_user_by_id
from ..models.user_model import UserModel

# 创建蓝图
user_bp = Blueprint('user_api', __name__, url_prefix='/api/user')
# 定义路由 

#暂时保留：目前不清楚用户信息保留位置
# @user_bp.route('/user/login', methods=['POST'])
# def login():
#     # 1. 获取前端传来的用户名和密码
#     data = request.get_json()
#     username = data.get("username", None)
#     password = data.get("password", None)

#     # 2. 从数据库查找用户并验证密码 (这里的验证逻辑是简化的)
#     user = UserModel.query.filter_by(username=username).first()
#     if user and user.check_password(password): # 假设 UserModel 中有 check_password 方法
#         # 3. 验证成功！为这个用户创建一个 Token
#         # 我们把用户的 ID 作为 Token 的 “身份标识 (identity)”
#         access_token = create_access_token(identity=user.id)
#         return jsonify(access_token=access_token)

#     return jsonify({"msg": "错误的用户名或密码"}), 401

@user_bp.route('/current', methods=['GET'])
@jwt_required() # 1. “关卡”：加上这个装饰器！
def get_current_user():
    from ..schemas.user_schema import UserSchema
    # 实例化 Schema
    user_schema = UserSchema()
    # 当请求到达时，@jwt_required() 会自动做几件事：
    #   a. 检查请求头里有没有 "Authorization: Bearer <token>"。
    #   b. 如果没有或 Token 无效，它会直接拒绝请求，返回 401 错误。
    #   c. 如果 Token 有效，它会解析出里面的身份标识 (identity)。
    
    # 2. “获取身份”：使用 get_jwt_identity() 函数拿到它！
    # 这个 identity 就是我们在登录时用 create_access_token(identity=user.id) 放进去的 user.id
    current_user_id = get_jwt_identity()
    
    # 3. 现在你拿到了用户的 ID，可以去数据库里查他的完整信息了
    user_object = get_user_by_id(current_user_id) # 调用我们之前写的 service 函数

    if user_object:
        response_data = user_schema.dump(user_object)
        return jsonify(response_data), 200
    else:
        return jsonify({"message": "未找到用户"}), 404