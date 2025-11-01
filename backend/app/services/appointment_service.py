# backend/app/services/appointment_service.py
from ..models.user_model import UserModel, DoctorModel
from ..models.appointment_model import AppointmentModel
from ..core.extensions import db
from datetime import datetime

def create_appointment(data, patient_user_id):
    """
    处理创建预约的业务逻辑
    """
    try:
        # 1. 验证医生是否存在
        # [cite: 1030]
        doctor = DoctorModel.query.get(data['doctorId'])
        if not doctor:
            return None, "医生不存在" # [cite: 1063]

        # 2. 验证患者是否存在 (通常 @jwt_required 已保证, 此处为双重检查)
        patient = UserModel.query.get(patient_user_id)
        if not patient or patient.role != 'patient':
            return None, "患者用户不存在"

        # 3. (核心) 组合预约时间
        # [cite: 1030]
        appointment_date = data['appointmentDate']
        appointment_time_str = data['appointmentTime'] # 例如 "上午"

        # 将 "上午" / "下午" 转换为具体时间
        appointment_hour = 9 # 默认为 9:00
        if "下午" in appointment_time_str:
            appointment_hour = 14 # 下午 2:00
        
        #
        appointment_datetime = datetime.combine(appointment_date, datetime.min.time()).replace(hour=appointment_hour)

        # 4. (TODO: 实际项目中应检查医生排班表)
        # 模拟检查医生是否可预约
        # if not is_doctor_available(doctor, appointment_datetime):
        #     return None, "所选日期不可预约" # [cite: 1058]

        # 5. 创建预约记录
        new_appointment = AppointmentModel(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_time=appointment_datetime,
            status='scheduled', 
            medical_record_id=data.get('medicalRecordId')
        )

        db.session.add(new_appointment)
        db.session.commit()

        return new_appointment, "预约成功"

    except Exception as e:
        db.session.rollback()
        return None, f"创建预约失败: {e}"