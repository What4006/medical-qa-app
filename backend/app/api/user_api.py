import os
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies, create_access_token
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from ..services.user_service import (
    get_user_by_id, 
    upload_user_avatar, 
    update_user_info, 
    change_password
)
from ..schemas.user_schema import ChangePasswordRequestSchema, UpdateUserInfoRequestSchema, UserSchema 
from ..core.extensions import db
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

ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg'} 
def allowed_avatar_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS

# --------------------------
# API #20: 获取用户详细信息 (GET /api/user/info)
# --------------------------

@user_bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info_api():
    """获取当前登录用户的详细信息"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)

        if not user:
            return jsonify({"error_code": 404, "message": "用户不存在"}), 404 

        # 构造响应数据
        response_data = {
            "fullname": user.full_name,
            "gender": user.gender,
            "birthday": user.birth_date.isoformat() if user.birth_date else None,
            "phone": user.phone, # <-- 关键修正：从独立的 phone 字段获取
            "idCard": user.id_card,
            "insuranceCard": user.insurance_card,
            "email": user.email,
            "pastHistory": user.basic_medical_history,
            "personalHistory": user.personal_history,
            "familyHistory": user.family_history,
            "avatar": user.avatar_url
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"Error in /api/user/info GET: {e}", exc_info=True)
        return jsonify({"error_code": 500, "message": "服务器内部错误，获取用户信息失败"}), 500

# --------------------------
# API #21: 上传用户头像 (POST /api/user/avatar)
# --------------------------
@user_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_user_avatar_api():
    """上传用户头像 [cite: 1079-1083]"""
    try:
        user_id = get_jwt_identity()

        if 'avatar' not in request.files:
            return jsonify({"error_code": 400, "message": "请求中未包含 avatar 文件部分"}), 400 

        file = request.files['avatar']

        if file.filename == '':
            return jsonify({"error_code": 400, "message": "未选择任何文件"}), 400

        if file and allowed_avatar_file(file.filename):
            # 1. 文件名处理
            filename = secure_filename(f"{user_id}_{datetime.utcnow().timestamp():.0f}_{file.filename}")
            
            # 2. 定义文件保存路径 
            upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path_on_disk = os.path.join(upload_folder, filename)
            file.save(file_path_on_disk)
            
            # 3. 数据库中保存相对路径
            db_file_path = os.path.join('uploads', 'avatars', filename).replace('\\', '/')

            # 4. 调用 service 更新数据库
            user, error_msg = upload_user_avatar(user_id, db_file_path)
            
            if not user:
                if os.path.exists(file_path_on_disk): os.remove(file_path_on_disk) 
                # [cite_start]失败响应 [cite: 1109-1112]
                return jsonify({"error_code": 500, "message": "服务器内部错误，头像更新失败"}), 500 
            
            # [cite_start]5. 成功返回新头像的 URL [cite: 1090-1096]
            return jsonify({"avatarUrl": db_file_path}), 200
        else:
            # [cite_start]失败响应 [cite: 1098-1102]
            return jsonify({"error_code": 400, "message": "请上传JPG或PNG格式的图片"}), 400

    except Exception as e:
        logging.error(f"Error in /api/user/avatar POST: {e}", exc_info=True)
        return jsonify({"error_code": 500, "message": "服务器内部错误，头像上传失败"}), 500

# --------------------------
# API #22: 更新用户个人信息 (PUT /api/user/info)
# --------------------------
@user_bp.route('/info', methods=['PUT'])
@jwt_required()
def update_user_info_api():
    """更新当前用户的个人信息"""
    try:
        user_id = get_jwt_identity()
        
        # 1. 验证请求数据
        data = UpdateUserInfoRequestSchema().load(request.json)
        
        # 2. 调用 service 层更新信息
        user, error_msg = update_user_info(user_id, data)
        
        if not user:
            return jsonify({"error_code": 400, "message": error_msg}), 400 

        # 3. 返回更新后的完整信息
        response_data = {
            "fullname": user.full_name,
            "gender": user.gender,
            "birthday": user.birth_date.isoformat() if user.birth_date else None,
            "phone": user.phone, # <-- 关键修正：从独立的 phone 字段获取
            "idCard": user.id_card,
            "insuranceCard": user.insurance_card,
            "email": user.email,
            "pastHistory": user.basic_medical_history,
            "personalHistory": user.personal_history,
            "familyHistory": user.family_history,
            "avatar": user.avatar_url
        }
        
        return jsonify(response_data), 200

    except ValidationError as err:
        logging.warning(f"更新信息数据校验失败: {err.messages}")
        first_error_msg = next(iter(err.messages.values()))[0] if err.messages else "请求数据格式错误"
        return jsonify({"error_code": 400, "message": f"数据验证错误: {first_error_msg}"}), 400
    except Exception as e:
        logging.error(f"Error in /api/user/info PUT: {e}", exc_info=True)
        return jsonify({"error_code": 500, "message": "服务器内部错误，更新用户信息失败"}), 500
    
# --------------------------
# API #23: 修改用户密码 (POST /api/user/change-password)
# --------------------------
@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password_api():
    """修改用户密码 [cite: 1160-1164]"""
    try:
        user_id = get_jwt_identity()
        
        # 1. 验证请求数据
        data = ChangePasswordRequestSchema().load(request.json)
        old_password = data['oldPassword']
        new_password = data['newPassword']
        
        # 2. 调用 service 层修改密码 (service 内部包含原密码和格式校验)
        user, error_msg = change_password(user_id, old_password, new_password)
        
        if not user:
            # [cite_start]400 for wrong old password or format error [cite: 1179-1188]
            return jsonify({"error_code": 400, "message": error_msg}), 400
        
        # [cite_start]3. 成功响应 [cite: 1172-1177]
        return jsonify({"message": "密码修改成功，请使用新密码登录"}), 200

    except ValidationError as err:
        logging.warning(f"修改密码数据校验失败: {err.messages}")
        first_error_msg = next(iter(err.messages.values()))[0] if err.messages else "请求数据格式错误"
        return jsonify({"error_code": 400, "message": f"数据验证错误: {first_error_msg}"}), 400
    except Exception as e:
        logging.error(f"Error in /api/user/change-password POST: {e}", exc_info=True)
        return jsonify({"error_code": 500, "message": "服务器内部错误，修改密码失败"}), 500


# --------------------------
# API #24: 用户退出登录 (POST /api/logout)
# --------------------------
@user_bp.route('/logout', methods=['POST']) 
@jwt_required()
def logout_api():
    """清除当前用户的登录状态（使 token 失效），退出系统 [cite: 1195-1199]"""
    # [cite_start]1. 返回成功 JSON [cite: 1207-1211]
    response = jsonify({"message": "已成功退出登录"})
    
    # 2. 使 JWT Cookie 失效
    unset_jwt_cookies(response)
    
    return response, 200