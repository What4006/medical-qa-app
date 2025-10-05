# backend/app/api/dev_api.py
#获取token：http://127.0.0.1:5000/api/dev/generate_token/

from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token
from ..core.extensions import db
from ..models.user_model import UserModel
from datetime import date

# 这是一个仅用于开发的蓝图
dev_bp = Blueprint('dev_api', __name__, url_prefix='/api/dev')

@dev_bp.route('/generate_token/<int:user_id>', methods=['GET'])
def generate_token_for_user(user_id):
    """
    一个升级版的开发者后门接口。
    它会为指定ID的用户生成一个有效的JWT Token。
    用法: GET /api/dev/generate_token/1  (为id=1的用户生成Token)
          GET /api/dev/generate_token/3  (为id=3的用户生成Token)
    """
    # 根据传入的 ID 查找用户
    user = UserModel.query.get(user_id)
    
    # 如果用户不存在，返回错误
    if not user:
        return jsonify({"message": f"错误：未找到ID为 {user_id} 的用户。"}), 404
    
    # 为这个用户创建一个Token (确保使用 str() )
    access_token = create_access_token(identity=str(user.id))
    
    # 返回Token和一些用户信息，方便确认
    return jsonify({
        "message": f"为用户 '{user.full_name}' (ID: {user.id}) 生成Token成功！",
        "user_id": user.id,
        "full_name": user.full_name,
        "access_token": access_token
    })