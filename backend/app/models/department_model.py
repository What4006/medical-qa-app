# backend/app/models/department_model.py
from ..core.extensions import db
from datetime import datetime # 引入 datetime 用于模拟 ID

class DepartmentModel(db.Model):
    __tablename__ = 'departments' # 定义表名

    # 使用自增整数 ID 作为主键更标准
    id = db.Column(db.Integer, primary_key=True)
    # 根据文档 API#15 的响应格式，模拟 dept-xxx 格式的 ID (虽然通常不推荐这样做)
    # 如果你想严格按照文档的 dept-xxx，可以考虑不在数据库中存这个字段，而在 Schema 中生成
    # department_code = db.Column(db.String(50), unique=True, nullable=False, default=lambda: f"dept-{hash(datetime.now())}")
    name = db.Column(db.String(100), unique=True, nullable=False, comment='科室名称')
    description = db.Column(db.Text, nullable=True, comment='科室描述')

    # 我们暂时不添加与 DoctorModel 的关系，以保持简单

    def __repr__(self):
        return f'<Department {self.name}>'