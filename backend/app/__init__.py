from flask import Flask
from .config import config
from .core.extensions import db, migrate, cors

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

    # 3. 导入并注册蓝图 (Blueprint)
    # 当你开始编写 API 时，会在这里取消注释
    # from .api.history_api import history_bp
    # app.register_blueprint(history_bp, url_prefix='/api/v1')

    # 4. 导入数据库模型，以便 Flask-Migrate 能够检测到它们
    # 这是让 `flask db migrate` 正常工作的关键一步
    # **已根据你的文件结构进行修正**
    from .models import user_model, consultation_model, appointment_model, review_model

    return app