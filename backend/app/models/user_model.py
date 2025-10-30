from datetime import datetime, date
from ..core.extensions import db # 从你的核心扩展文件中导入db实例
# 如果你使用密码哈希，可能需要 werkzeug
from werkzeug.security import generate_password_hash, check_password_hash

# --- 用户与医生模型 (建议放入 user_model.py) ---

class UserModel(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名，用于登录')
    password_hash = db.Column(db.String(256), nullable=False, comment='加密后的密码')
    role = db.Column(db.String(10), nullable=False, default='patient', comment="角色 ('patient', 'doctor')")
    full_name = db.Column(db.String(100), comment='真实姓名')
    gender = db.Column(db.String(10), comment='性别')
    birth_date = db.Column(db.Date, comment='出生日期') 
    basic_medical_history = db.Column(db.Text, comment='基础疾病史')
    personal_history = db.Column(db.Text, nullable=True, comment='个人史 ')
    family_history = db.Column(db.Text, nullable=True, comment='家族史')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='账户创建时间')

    # --- 新增一个属性，用于动态计算年龄 ---
    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        # 计算年龄的精确逻辑
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    # 关系定义：一个用户可以是一个医生 (一对一)
    doctor_info = db.relationship('DoctorModel', backref='user', uselist=False, cascade="all, delete-orphan")
    # 关系定义：一个病人可以有多次AI问诊 (一对多)
    ai_consultations = db.relationship('AIConsultationModel', backref='patient', lazy=True)
    # 关系定义：一个病人可以有多次预约 (一对多)
    appointments = db.relationship('AppointmentModel', backref='patient', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DoctorModel(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, comment='关联的用户ID')
    title = db.Column(db.String(50), comment='职称')
    specialty = db.Column(db.String(50), comment='科室/专业')
    bio = db.Column(db.Text, comment='个人简介/擅长领域')
    rating = db.Column(db.Float, comment='综合评分')
    review_count = db.Column(db.Integer, comment='评价数量')
    available_slots = db.Column(db.JSON, comment='可预约时间段')

    # --- 新增以下字段以匹配文档要求 ---(匹配医生注册的内容)
    #图片存储是通过新增字段来保存URL，任然是mysql数据库
    # 实际图片文件存储在服务器或云存储中
    hospital = db.Column(db.String(100), comment='所属医院')
    license_id = db.Column(db.String(100), unique=True, comment='15位执业医师证号')
    certificate_image_url = db.Column(db.String(255), comment='资质证明图片路径')
    
    # --- 关系定义保持不变 ---
    appointments = db.relationship('AppointmentModel', backref='doctor', lazy=True)
    reviews = db.relationship('DoctorReviewModel', backref='doctor', lazy=True)