import pytest
import io
from flask_jwt_extended import create_access_token
from app.models.user_model import UserModel, DoctorModel
from app.core.extensions import db
from datetime import datetime, date

# --- Fixtures for Auth API Tests ---

@pytest.fixture(scope='function')
def patient_payload():
    """提供一个标准的患者注册数据负载"""
    return {
        "phone": "13800138000",
        "password": "Password123",
        "full_name": "测试患者",
        "birth_date": "1990-01-15"
    }

@pytest.fixture(scope='function')
def doctor_payload():
    """提供一个标准的医生注册数据负载 (不含文件)"""
    return {
        "phone": "13900139000",
        "password": "DoctorPassword123",
        "full_name": "测试医生",
        "license_id": "123456789012345",
        "hospital": "测试医院",
        "department": "测试科室",
        "title": "主治医师"
    }

# --- Patient Registration Tests ---

def test_register_patient_success(test_client, patient_payload):
    """测试场景: 成功注册一个新患者"""
    response = test_client.post('/api/auth/register/patient', json=patient_payload)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json['code'] == 200
    assert "患者注册成功" in response_json['msg']

def test_register_patient_duplicate_phone(test_client, patient_payload):
    """测试场景: 使用已存在的手机号注册患者应失败"""
    # 第一次注册 (应该成功)
    test_client.post('/api/auth/register/patient', json=patient_payload)
    # 第二次使用相同手机号注册
    response = test_client.post('/api/auth/register/patient', json=patient_payload)
    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json['code'] == 400
    assert "手机号已被注册" in response_json['msg']

# --- Doctor Registration Tests ---

def test_register_doctor_success(test_client, doctor_payload):
    """测试场景: 成功注册一个新医生 (包含文件上传)"""
    # 模拟文件上传
    doctor_payload['certificate'] = (io.BytesIO(b"fake image data"), 'test.jpg')
    
    response = test_client.post(
        '/api/auth/register/doctor',
        content_type='multipart/form-data',
        data=doctor_payload
    )
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json['code'] == 200
    assert "医生注册成功" in response_json['msg']

def test_register_doctor_missing_file(test_client, doctor_payload):
    """测试场景: 注册医生时未上传证书文件应失败"""
    response = test_client.post(
        '/api/auth/register/doctor',
        content_type='multipart/form-data',
        data=doctor_payload # 没有 'certificate' 字段
    )
    response_json = response.get_json()

    assert response.status_code == 400
    assert "文件部分" in response_json['msg']

# --- Login Tests ---

def test_login_patient_success(test_client, test_app, patient_payload):
    """测试场景: 已注册的患者成功登录"""
    # 先注册
    test_client.post('/api/auth/register/patient', json=patient_payload)
    
    login_data = {
        "phone": patient_payload['phone'],
        "password": patient_payload['password'],
        "user_type": 1 # 1 代表患者
    }
    response = test_client.post('/api/auth/login', json=login_data)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json['code'] == 200
    assert "登录成功" in response_json['msg']
    assert "token" in response_json['data']

def test_login_doctor_success(test_client, test_app, doctor_payload):
    """测试场景: 已注册的医生成功登录"""
    # 先注册医生
    doctor_payload['certificate'] = (io.BytesIO(b"fake image data"), 'test.jpg')
    test_client.post('/api/auth/register/doctor', content_type='multipart/form-data', data=doctor_payload)

    login_data = {
        "phone": doctor_payload['phone'],
        "password": doctor_payload['password'],
        "user_type": 2 # 2 代表医生
    }
    response = test_client.post('/api/auth/login', json=login_data)
    response_json = response.get_json()
    
    assert response.status_code == 200
    assert "token" in response_json['data']

def test_login_wrong_password(test_client, patient_payload):
    """测试场景: 使用错误的密码登录应失败"""
    test_client.post('/api/auth/register/patient', json=patient_payload)
    
    login_data = {
        "phone": patient_payload['phone'],
        "password": "wrongpassword",
        "user_type": 1
    }
    response = test_client.post('/api/auth/login', json=login_data)
    response_json = response.get_json()

    assert response.status_code == 401
    assert "用户名或密码错误" in response_json['msg']

# --- Get Me (/api/auth/me) Tests ---

def test_get_me_patient(test_client, test_app):
    """测试场景: 登录后，患者能成功获取自己的信息"""
    # 准备一个已存在的患者用户
    with test_app.app_context():
        patient = UserModel(id=101, username='13812345678', role='patient', full_name='患者王五', birth_date=date(1995,5,20))
        patient.set_password('password')
        db.session.add(patient)
        db.session.commit()
        # 创建 token
        access_token = create_access_token(identity=str(patient.id))

    headers = {'Authorization': f'Bearer {access_token}'}
    response = test_client.get('/api/auth/me', headers=headers)
    response_json = response.get_json()

    # 在断言前添加一个打印，方便调试
    if response.status_code != 200:
        print("服务器返回的错误信息:", response_json)

    assert response.status_code == 200
    assert response_json['code'] == 200
    assert response_json['data']['phone'] == '13812345678'
    assert response_json['data']['user_type'] == 1
    assert 'patient_info' in response_json['data']
    assert 'doctor_info' not in response_json['data']

def test_get_me_doctor(test_client, test_app):
    """测试场景: 登录后，医生能成功获取自己的信息"""
    with test_app.app_context():
        doctor_user = UserModel(id=202, username='13987654321', role='doctor', full_name='医生赵六')
        doctor_user.set_password('password')
        doctor_info = DoctorModel(user=doctor_user, specialty='心内科', hospital='测试医院二')
        db.session.add_all([doctor_user, doctor_info])
        db.session.commit()
        access_token = create_access_token(identity=str(doctor_user.id))

    headers = {'Authorization': f'Bearer {access_token}'}
    response = test_client.get('/api/auth/me', headers=headers)
    response_json = response.get_json()

    # 在断言前添加一个打印，方便调试
    if response.status_code != 200:
        print("服务器返回的错误信息:", response_json)

    assert response.status_code == 200
    assert response_json['data']['user_type'] == 2
    assert 'doctor_info' in response_json['data']
    assert response_json['data']['doctor_info']['department'] == '心内科'
    assert 'patient_info' not in response_json['data']

def test_get_me_unauthorized(test_client):
    """测试场景: 未提供 Token 访问受保护的 /me 接口应失败"""
    response = test_client.get('/api/auth/me')
    assert response.status_code == 401