# backend/app/services/medical_record_service.py
from ..models.medical_record_model import MedicalRecordModel
from ..core.extensions import db

def get_records_for_patient(patient_id):
    """
    获取指定患者的所有病历记录
    
    """
    #
    return MedicalRecordModel.query.filter_by(
        patient_id=patient_id
    ).order_by(MedicalRecordModel.created_at.desc()).all()

def get_record_detail(patient_id, record_id):
    """
    获取单条病历详情，同时验证该病历是否属于该患者
    
    """
    #
    return MedicalRecordModel.query.filter_by(
        id=record_id,
        patient_id=patient_id
    ).first()