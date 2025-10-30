# backend/app/api/department_api.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required # 引入 jwt_required 以保护路由
from ..services import department_service # 导入服务层函数
from ..schemas.department_schema import DepartmentSchema # 导入 Schema
import logging # 引入日志记录

# 创建蓝图，指定名称和 URL 前缀 /api/departments
department_bp = Blueprint('department_api', __name__, url_prefix='/api/departments')

# 定义 GET 请求的路由，路径就是蓝图的根路径 ('')
@department_bp.route('', methods=['GET'])
@jwt_required() # 添加装饰器，要求请求必须带有有效的 JWT Token
def get_departments():
    """获取科室列表 API"""
    try:
        # 1. 调用服务层函数获取数据
        departments = department_service.get_all_departments()

        # 2. 实例化 Schema，因为要序列化列表，设置 many=True
        schema = DepartmentSchema(many=True)

        # 3. 使用 Schema 序列化数据
        result = schema.dump(departments)

        # 4. 返回 JSON 响应和 200 OK 状态码
        return jsonify(result), 200
    except Exception as e:
        # 记录详细错误日志
        logging.error(f"Error in /api/departments GET: {e}", exc_info=True)
        # 返回标准的错误响应
        return jsonify({"error_code": 500, "message": "获取科室列表失败"}), 500