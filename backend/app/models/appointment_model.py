from datetime import datetime
from ..core.extensions import db # 从你的核心扩展文件中导入db实例
# 如果你使用密码哈希，可能需要 werkzeug
from werkzeug.security import generate_password_hash, check_password_hash

class AppointmentModel(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='关联的病人ID')
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, comment='关联的医生ID')
    appointment_time = db.Column(db.DateTime, nullable=False, comment='预约的日期和时间')
    status = db.Column(db.String(20), default='scheduled', comment="状态 ('scheduled', 'completed', 'canceled')")
    is_urgent = db.Column(db.Boolean, default=False, comment='是否为加急')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='预约创建时间')