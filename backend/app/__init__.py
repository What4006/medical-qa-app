from flask import Flask
from .config import config
from .core.extensions import db, migrate, cors, ma
from flask_jwt_extended import JWTManager  #  导入 JWTManager

def create_app(config_name='default'):
    """
    应用工厂函数，用于创建 Flask app 实例。
    """
    app = Flask(__name__)

    # 1. 从配置对象中加载配置
    app.config.from_object(config[config_name])

    # 2. 初始化扩展
    # 将在 extensions.py 中创建的扩展实例与 app 关联
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, supports_credentials=True)
    ma.init_app(app)
    jwt = JWTManager(app)

    # 3. 导入并注册蓝图 (Blueprint)
    from .api.user_api import user_bp
    app.register_blueprint(user_bp)

    # 4. 导入数据库模型，以便 Flask-Migrate 能够检测到它们
    # 这是让 `flask db migrate` 正常工作的关键一步
    from .models import user_model, consultation_model, appointment_model, review_model

    return app