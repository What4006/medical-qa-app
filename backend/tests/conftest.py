import pytest
from app import create_app # 从您的应用工厂导入 create_app
from app.core.extensions import db

@pytest.fixture(scope='function')
def test_app():
    """创建一个测试用的 Flask app 实例"""
    # 使用'testing'配置来创建app，例如使用一个独立的测试数据库
    app = create_app('testing') 
    
    # 'yield' 之前的代码是“准备”阶段
    with app.app_context():
        # 这里可以进行一些数据库的初始化设置
        db.create_all() 
        yield app 
        # 'yield' 之后的代码是“清理”阶段
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def test_client(test_app):
    """
    为每一个测试函数创建一个全新的测试客户端。
    """
    return test_app.test_client()