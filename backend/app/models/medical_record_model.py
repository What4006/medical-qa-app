# backend/app/models/medical_record_model.py

from datetime import datetime
from ..core.extensions import db # 导入 db 实例

class MedicalRecordModel(db.Model):
    __tablename__ = 'medical_records' # 定义表名

    # 根据文档 API #19 定义字段
    id = db.Column(db.Integer, primary_key=True) # 病历记录的唯一 ID
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='关联的病人ID') # 关联到 User 模型

    # 使用 Text 类型存储可能较长的文本描述
    chief_complaint = db.Column(db.Text, nullable=True, comment='主诉')
    history_present_illness = db.Column(db.Text, nullable=True, comment='现病史')
    past_medical_history = db.Column(db.Text, nullable=True, comment='既往史')
    personal_history = db.Column(db.Text, nullable=True, comment='个人史')
    family_history = db.Column(db.Text, nullable=True, comment='家族史')
    diagnosis = db.Column(db.Text, nullable=True, comment='诊断结果')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='病历创建时间')

    # 添加关系，方便从 User 模型访问病历 (可选，但推荐)
    patient = db.relationship('UserModel', backref=db.backref('medical_records', lazy=True))

    def __repr__(self):
        return f'<MedicalRecord {self.id} for Patient {self.patient_id}>'