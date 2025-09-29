from datetime import datetime
from ..models.user_model import UserModel, DoctorModel
from ..core.extensions import db

def register_patient(data):
    """处理患者注册逻辑"""
    # 检查用户名（手机号）是否已存在
    if UserModel.query.filter_by(username=data['username']).first():
        return None, "手机号已被注册"

    new_user = UserModel(
        username=data['username'],
        role='patient',
        full_name=data['full_name'],
        birth_date=data['birth_date']
    )
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return new_user, "患者注册成功，请登录"

def register_doctor(data, certificate_path):
    """处理医生注册逻辑，包含资质文件路径"""
    # 检查手机号是否已存在
    if UserModel.query.filter_by(username=data['phone']).first():
        return None, "手机号已被注册"
        
    # 检查执业医师证号是否已存在
    if DoctorModel.query.filter_by(license_id=data['license_id']).first():
        return None, "执业医师证号已被注册"

    # 1. 创建 UserModel 基础用户
    new_user = UserModel(
        username=data['phone'],
        role='doctor',
        full_name=data['full_name']
    )
    new_user.set_password(data['password'])
    
    # 2. 创建关联的 DoctorModel 信息，并存入证书路径
    new_doctor_info = DoctorModel(
        title=data['title'],
        specialty=data['department'], # 注意字段名映射
        hospital=data['hospital'],
        license_id=data['license_id'],
        certificate_image_url=certificate_path, # 保存文件路径
        user=new_user
    )

    db.session.add(new_user)
    db.session.add(new_doctor_info)
    db.session.commit()

    return new_user, "医生注册成功，等待审核通过后即可登录"

def login_user(data):
    """处理用户登录逻辑"""
    user_role = 'patient' if data['user_type'] == 1 else 'doctor'
    
    user = UserModel.query.filter_by(username=data['username'], role=user_role).first()

    if user and user.check_password(data['password']):
        return user
    
    return None