from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..services.user_service import get_user_by_id
from ..models.user_model import UserModel

# 创建蓝图
user_bp = Blueprint('user_api', __name__, url_prefix='/api/user')
# 定义路由 

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