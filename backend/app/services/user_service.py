#9.23——用于实现获取当前用户信息的API--w4006
from ..models.user_model import UserModel 
from ..core.extensions import db
from datetime import datetime
import re 
import logging

def get_user_by_id(user_id):
    #在数据库里查找用户
    user=UserModel.query.get(user_id)
    return user

def upload_user_avatar(user_id, avatar_path):
    """
    API #21: 上传用户头像 service
    """
    user = UserModel.query.get(user_id)
    if not user:
        return None, "用户不存在"
    
    try:
        user.avatar_url = avatar_path
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in upload_user_avatar: {e}")
        return None, f"数据库更新失败: {e}"

def update_user_info(user_id, data):
    """
    API #22: 更新用户个人信息 service
    """
    user = UserModel.query.get(user_id)
    if not user:
        return None, "用户不存在"
    
    try:
        # 0. 关键字段唯一性检查 (手机号、邮箱、身份证号)
        # 检查新的 phone 是否已被使用
        if user.phone != data['phone'] and UserModel.query.filter_by(phone=data['phone']).first():
             return None, "新的手机号已被注册"
        # 检查 email 是否已被使用
        if user.email != data['email'] and UserModel.query.filter_by(email=data['email']).first():
            return None, "邮箱已被其他用户使用"
        # 检查 id_card 是否已被使用
        if user.id_card != data['idCard'] and UserModel.query.filter_by(id_card=data['idCard']).first():
            return None, "身份证号已被其他用户使用"
        
        # 1. 更新基础信息
        user.full_name = data['fullname']
        user.gender = data['gender']
        user.birth_date = data['birthday']
        user.phone = data['phone'] # <-- 关键修正：更新独立的 phone 字段
        
        # 2. 更新身份信息
        user.id_card = data['idCard']
        user.email = data['email']
        user.insurance_card = data.get('insuranceCard')
             
        # 3. 更新病史信息
        user.basic_medical_history = data.get('pastHistory')
        user.personal_history = data.get('personalHistory')
        user.family_history = data.get('familyHistory')
        
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in update_user_info: {e}")
        return None, f"更新失败，请检查输入数据是否重复或格式正确: {e}"
    
def change_password(user_id, old_password, new_password):
    """
    API #23: 修改用户密码 service
    """
    user = UserModel.query.get(user_id)
    if not user:
        return None, "用户不存在"
        
    # 1. 验证原密码
    if not user.check_password(old_password):
        return None, "原密码错误，请重新输入" 

    # 2. 校验新密码格式 (包含字母和数字)
    if not (re.search(r'[a-zA-Z]', new_password) and re.search(r'\d', new_password)):
        return None, "新密码需包含字母和数字，且长度不少于8位"
        
    # 3. 设置新密码
    user.set_password(new_password)
    
    db.session.add(user)
    db.session.commit()
    return user, "密码修改成功"