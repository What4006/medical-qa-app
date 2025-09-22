from datetime import datetime
from ..core.extensions import db # 从你的核心扩展文件中导入db实例
# 如果你使用密码哈希，可能需要 werkzeug
from werkzeug.security import generate_password_hash, check_password_hash

class AIConsultationModel(db.Model):
    __tablename__ = 'ai_consultations'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='关联的病人ID')
    status = db.Column(db.String(20), default='in_progress', comment="状态 ('in_progress', 'completed', 'pending_review', 'reviewed')")
    symptom_description = db.Column(db.Text, comment='病人提交的详细症状描述')
    structured_symptoms = db.Column(db.JSON, comment='结构化的症状信息')
    ai_diagnosis = db.Column(db.String(255), comment='AI初步诊断结果')
    ai_confidence = db.Column(db.Float, comment='AI诊断的匹配度')
    ai_analysis = db.Column(db.Text, comment='AI给出的详细分析')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='问诊创建时间')
    
    # 关系定义：一次问诊包含多条聊天消息 (一对多)
    chat_messages = db.relationship('ChatMessageModel', backref='consultation', lazy=True, cascade="all, delete-orphan")
    # 关系定义：一次问诊只有一个审核记录 (一对一)
    review = db.relationship('DoctorReviewModel', backref='consultation', uselist=False, cascade="all, delete-orphan")

class ChatMessageModel(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey('ai_consultations.id'), nullable=False, comment='关联的AI问诊ID')
    sender_type = db.Column(db.String(10), nullable=False, comment="发送方 ('user' 或 'ai')")
    content = db.Column(db.Text, nullable=False, comment='消息内容')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, comment='消息发送时间')