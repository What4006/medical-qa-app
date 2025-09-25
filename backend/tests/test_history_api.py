#9.26 新增测试用例，覆盖历史记录接口的不同场景 --4006
import pytest
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta

# 导入所有需要的模型和 db 实例
from app.models.user_model import UserModel
from app.models.consultation_model import AIConsultationModel, DoctorConsultationModel
from app.core.extensions import db

# --- 准备测试数据用的 Fixtures ---

@pytest.fixture(scope='function')
def seed_users(test_app):
    """
    在数据库中准备一个病人和一个医生，用于测试。
    返回一个包含他们ID的字典。
    """
    with test_app.app_context():
        patient = UserModel(id=1, username='patient1', role='patient', full_name='病人张三')
        patient.set_password('password')
        
        doctor = UserModel(id=2, username='doctor1', role='doctor', full_name='李医生')
        doctor.set_password('password')

        db.session.add_all([patient, doctor])
        db.session.commit()
        yield {'patient_id': patient.id, 'doctor_id': doctor.id}
        db.session.remove()

# --- 测试用例 ---

def test_get_recent_when_ai_is_latest(test_client, test_app, seed_users):
    """
    测试场景1: 当最新的记录是 AI 问诊时
    """
    patient_id = seed_users['patient_id']
    with test_app.app_context():
        # 准备数据：AI 问诊记录是 1 小时前，医生问诊记录是 2 小时前
        ai_record = AIConsultationModel(patient_id=patient_id, created_at=datetime.utcnow() - timedelta(hours=1), ai_diagnosis="感冒", ai_analysis="多喝热水")
        doctor_record = DoctorConsultationModel(patient_id=patient_id, doctor_id=seed_users['doctor_id'], created_at=datetime.utcnow() - timedelta(hours=2), appointment_time=datetime.utcnow() - timedelta(hours=2), patient_symptoms="头痛", doctor_diagnosis="休息一下")
        db.session.add_all([ai_record, doctor_record])
        db.session.commit()
        
        # 为病人创建 Token
        access_token = create_access_token(identity=str(patient_id))

    headers = {'Authorization': f'Bearer {access_token}'}
    response = test_client.get('/api/history/recent', headers=headers)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json['type'] == 'ai'
    assert response_json['title'] == '感冒'

def test_get_recent_when_doctor_is_latest(test_client, test_app, seed_users):
    """
    测试场景2: 当最新的记录是医生问诊时
    """
    patient_id = seed_users['patient_id']
    doctor_id = seed_users['doctor_id']
    with test_app.app_context():
        # 准备数据：AI 问诊记录是 2 小时前，医生问诊记录是 1 小时前
        ai_record = AIConsultationModel(patient_id=patient_id, created_at=datetime.utcnow() - timedelta(hours=2), ai_diagnosis="感冒", ai_analysis="多喝热水")
        doctor_record = DoctorConsultationModel(patient_id=patient_id, doctor_id=doctor_id, created_at=datetime.utcnow() - timedelta(hours=1), appointment_time=datetime.utcnow() - timedelta(hours=1), patient_symptoms="头痛", doctor_diagnosis="休息一下", department="内科")
        db.session.add_all([ai_record, doctor_record])
        db.session.commit()

        access_token = create_access_token(identity=str(patient_id))

    headers = {'Authorization': f'Bearer {access_token}'}
    response = test_client.get('/api/history/recent', headers=headers)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json['type'] == 'doctor'
    assert response_json['title'] == '头痛'
    assert response_json['doctor'] == '李医生'

def test_get_recent_with_no_records(test_client, test_app, seed_users):
    """
    测试场景3: 当用户没有任何问诊记录时
    """
    patient_id = seed_users['patient_id']
    with test_app.app_context():
        # 不创建任何问诊记录
        access_token = create_access_token(identity=str(patient_id))

    headers = {'Authorization': f'Bearer {access_token}'}
    response = test_client.get('/api/history/recent', headers=headers)
    
    assert response.status_code == 200
    assert response.get_json() is None # API 应返回 null

def test_get_recent_unauthorized(test_client):
    """
    测试场景4: 未提供认证 Token
    """
    response = test_client.get('/api/history/recent')
    assert response.status_code == 401