import os
from dotenv import load_dotenv
from datetime import timedelta

# 加载 .env 文件中的环境变量
load_dotenv()

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 正确的 PyMySQL 驱动格式是 'mysql+pymysql'。
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Tyj317050@127.0.0.1/medical_qa_app_db?charset=utf8mb4'

class TestingConfig(Config):
    """
    测试环境配置
    """
    TESTING = True # 开启测试模式
    # 使用内存中的 SQLite 数据库，速度最快，每次测试都是全新的数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    # 在测试环境中禁用 CSRF 保护，因为测试客户端处理 CSRF cookies 很麻烦
    JWT_CSRF_PROTECTION = False
    # --- 添加下面这一行，以明确禁用 Flask-WTF 的 CSRF 功能 ---
    # 这样可以防止任何隐式的 CSRF 启用
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    # 生产环境的连接字符串应该总是从环境变量中获取，以保证安全
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # 在生产环境中可以添加更多配置...

# 创建一个配置字典，方便在 create_app 中根据字符串选择配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}