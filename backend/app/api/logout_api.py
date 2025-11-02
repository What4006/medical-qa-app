# backend/app/api/logout_api.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, unset_jwt_cookies
import logging

# API #24: 用户退出登录 - 路由: /api/logout
# 创建一个无前缀的蓝图
logout_bp = Blueprint('logout_api', __name__)

# 路由同时处理 POST (实际请求) 和 OPTIONS (预检请求)
@logout_bp.route('/api/logout', methods=['POST', 'OPTIONS'])
@jwt_required()
def logout_api_function():
    """API #24: 清除当前用户的登录状态（使 token 失效），退出系统"""
    
    # 1. 关键：处理 CORS 预检请求 (OPTIONS)，返回 200 OK
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # 2. 处理实际的 POST 退出请求
        response = jsonify({"message": "已成功退出登录"})
        
        # 清除 JWT cookies (如果使用了 cookie)
        unset_jwt_cookies(response)
        
        return response, 200

    except Exception as e:
        logging.error(f"Error in /api/logout POST: {e}", exc_info=True)
        return jsonify({"error_code": 500, "message": "服务器内部错误，退出登录失败"}), 500