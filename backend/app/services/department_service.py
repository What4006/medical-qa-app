# backend/app/services/department_service.py
from ..models.department_model import DepartmentModel # 导入我们刚创建的模型
from ..core.extensions import db
import logging # 引入日志记录

def get_all_departments():
    """获取所有科室列表"""
    try:
        # 查询所有科室记录，并按名称排序
        departments = DepartmentModel.query.order_by(DepartmentModel.name).all()
        return departments
    except Exception as e:
        # 记录错误日志
        logging.error(f"Error fetching departments: {e}")
        # 可以在这里根据需要决定是返回空列表还是抛出异常
        return [] # 出错时返回空列表，避免 API 崩溃