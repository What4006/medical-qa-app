import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 正确的 PyMySQL 驱动格式是 'mysql+pymysql'。
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:@127.0.0.1/medical_qa_app_db?charset=utf8mb4'

class ProductionConfig(Config):
    """生产环境配置"""
    # 生产环境的连接字符串应该总是从环境变量中获取，以保证安全
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # 在生产环境中可以添加更多配置...

# 创建一个配置字典，方便在 create_app 中根据字符串选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}