import os
# --- 核心修改：在所有其他导入之前，首先加载 .env 文件 ---
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.core.extensions import db
from app.models import user_model, consultation_model, appointment_model, review_model

# 根据环境变量创建 app, 默认为 'default' (开发环境)
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """为 flask shell 命令自动导入常用对象"""
    return dict(
        db=db,
        UserModel=user_model.UserModel,
        DoctorModel=user_model.DoctorModel,
        AIConsultationModel=consultation_model.AIConsultationModel,
        ChatMessageModel=consultation_model.ChatMessageModel,
        AppointmentModel=appointment_model.AppointmentModel,
        DoctorReviewModel=review_model.DoctorReviewModel
    )