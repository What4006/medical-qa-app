# backend/app/services/doctor_service.py
from ..models.user_model import DoctorModel, UserModel
from ..models.department_model import DepartmentModel
from ..core.extensions import db
import logging

def get_doctors(department_id=None):
    """
    获取医生列表，支持按科室ID筛选。
    """
    try:
        # 基础查询，关联 UserModel 以便后续获取姓名
        query = DoctorModel.query.join(UserModel, DoctorModel.user_id == UserModel.id)
        
        # [cite: 1606]
        if department_id:
            # 1. 根据科室ID查询科室名称
            department = DepartmentModel.query.get(department_id) #
            
            if department:
                # 2. 使用科室名称过滤医生的 'specialty' 字段
                # (假设 DoctorModel.specialty 存储的是科室名称)
                query = query.filter(DoctorModel.specialty == department.name) #
            else:
                # 如果传入的 departmentId 无效，返回空列表
                return []
        
        doctors = query.all()
        return doctors

    except Exception as e:
        logging.error(f"Error fetching doctors: {e}", exc_info=True)
        return []