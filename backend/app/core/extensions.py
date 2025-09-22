# backend/app/core/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# 1. 实例化 SQLAlchemy，用于操作数据库 ORM
# 这个 db 对象需要被你的 models 文件导入，用来定义数据模型
db = SQLAlchemy()

# 2. 实例化 Migrate，用于管理数据库迁移
# 它需要 db 对象和 app 对象才能完成初始化
migrate = Migrate()

# 3. 实例化 CORS，用于处理跨域请求
# 你的前端和后端很可能运行在不同的端口上，需要它来允许浏览器正常通信
cors = CORS()
