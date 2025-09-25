import pytest
from flask_jwt_extended import create_access_token
from app.models.user_model import UserModel
from app.core.extensions import db

@pytest.fixture(scope='function')
def seed_user(test_app):
    """
    这是一个新的 Fixture，专门负责在数据库中“播种”一个用户。
    它会在每个需要它的测试函数运行前，准备好一个干净的用户数据。
    """
    with test_app.app_context():
        test_user = UserModel(
            id=1,
            username='testuser',
            role='patient',
            full_name='张先生'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        # 返回用户的ID，方便后续创建Token
        yield test_user.id
        # yield 之后的代码是清理阶段，虽然 conftest 已经有 drop_all，
        # 但在这里明确 remove 可以增强隔离性。
        db.session.remove()


def test_get_current_user_success(test_client, test_app, seed_user):
    """
    测试：在提供了有效Token的情况下，成功获取用户信息
    """
    # Arrange (准备阶段)
    # `seed_user` fixture 已经自动运行，并在数据库中创建了用户。
    # `seed_user` 的返回值 (user_id) 被 pytest 注入到了这个函数中。
    user_id = seed_user

    # 在一个 app_context 中为这个用户创建一个有效的 access_token
    with test_app.app_context():
        # --- 关键修改：将整数 ID 转换为字符串 ---
        access_token = create_access_token(identity=str(user_id))
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Act (执行阶段)
    response = test_client.get('/api/user/current', headers=headers)
    
    # Assert (断言阶段)
    # 增加一个打印，方便在失败时看到服务器返回的具体错误信息
    if response.status_code != 200:
        print("服务器返回的错误信息:", response.get_json())
        
    assert response.status_code == 200
    response_json = response.get_json()
    assert 'nickname' in response_json
    assert response_json['nickname'] == '张先生'

def test_get_current_user_no_token(test_client):
    """
    测试：在没有提供Token的情况下，访问受保护接口应该失败
    """
    response = test_client.get('/api/user/current')
    assert response.status_code == 401
