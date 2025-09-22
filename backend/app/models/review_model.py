from datetime import datetime
from ..core.extensions import db # 从你的核心扩展文件中导入db实例
# 如果你使用密码哈希，可能需要 werkzeug
from werkzeug.security import generate_password_hash, check_password_hash

class DoctorReviewModel(db.Model):
    __tablename__ = 'doctor_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('ai_consultations.id'), nullable=False, unique=True, comment='关联的AI问诊ID')
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, comment='审核的医生ID')
    is_approved = db.Column(db.Boolean, comment='审核结果 (True: 确认)')
    doctor_diagnosis = db.Column(db.Text, comment='医生修改后的诊断')
    comments = db.Column(db.Text, comment='医生的审核意见')
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow, comment='审核完成的时间')