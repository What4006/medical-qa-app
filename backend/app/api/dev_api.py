# backend/app/api/dev_api.py
#获取token：http://127.0.0.1:5000/api/dev/generate_test_token
from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token
from ..core.extensions import db
from ..models.user_model import UserModel
from datetime import date

# 这是一个仅用于开发的蓝图
dev_bp = Blueprint('dev_api', __name__, url_prefix='/api/dev')

@dev_bp.route('/generate_test_token', methods=['GET'])
def generate_test_token():
    """
    一个用于开发的后门接口。
    它会查找或创建一个固定的测试患者，并返回一个有效的JWT Token。
    """
    # 定义测试用户的信息
    test_username = 'testpatient@example.com'
    test_full_name = '测试患者'
    
    # 查找测试用户是否存在
    user = UserModel.query.filter_by(username=test_username).first()
    
    # 如果用户不存在，就创建一个
    if not user:
        user = UserModel(
            username=test_username,
            role='patient',
            full_name=test_full_name,
            birth_date=date(1995, 10, 1) # 添加一个出生日期用于测试年龄计算
        )
        user.set_password('password') # 设置一个默认密码
        db.session.add(user)
        db.session.commit()
    
    # 为这个用户创建一个Token
    access_token = create_access_token(identity=str(user.id))
    
    # 返回Token和一些用户信息，方便确认
    return jsonify({
        "message": "测试Token生成成功，请在浏览器开发者工具中使用。",
        "user_id": user.id,
        "full_name": user.full_name,
        "access_token": access_token
    })