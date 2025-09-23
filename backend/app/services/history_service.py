#9.23——用于  获取最近问诊记录  的API--w4006
from ..models.consultation_model import AIConsultationModel, DoctorConsultationModel

def get_recent_consultation(user_id):
    recent_record_ai=AIConsultationModel.query.filter_by(patient_id=user_id).order_by(AIConsultationModel.created_at.desc()).first()
    recent_record_doctor =DoctorConsultationModel.query.filter_by(patient_id=user_id).order_by(DoctorConsultationModel.created_at.desc()).first()
    if recent_record_ai and recent_record_doctor:
        if recent_record_ai.created_at > recent_record_doctor.created_at:
            return recent_record_ai
        else:
            return recent_record_doctor
    elif recent_record_ai:
        return recent_record_ai
    elif recent_record_doctor:
        return recent_record_doctor
    else:
        return None