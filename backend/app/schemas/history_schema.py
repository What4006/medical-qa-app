#9.23——用于  获取最近问诊记录  的API--w4006
from ..core.extensions import ma
from marshmallow import fields

class AiConsultationSchema(ma.Schema):
    class Meta:
        # "id" 直接从模型的 id 字段获取
        id = fields.Int()

        # "type" 在模型中不存在，但 API 要求返回 'ai'，我们在这里固定它
        type = fields.Constant("ai")
        
        # "title" 对应模型的 "ai_diagnosis" 字段
        title = fields.Str(attribute="ai_diagnosis")
        
        # "date" 从模型的 "created_at" 字段中格式化提取
        date = fields.DateTime(attribute="created_at", format="%Y-%m-%d")
        
        # "time" 也从模型的 "created_at" 字段中格式化提取
        time = fields.DateTime(attribute="created_at", format="%H:%M")
        
        # "status" 直接从模型的 status 字段获取
        status = fields.Str()
        
        # "summary" 对应模型的 "ai_analysis" 字段
        summary = fields.Str(attribute="ai_analysis")

class DoctorConsultationSchema(ma.Schema):
    # --- 字段映射: API 字段名 <---> DoctorConsultationModel 属性 ---

    id = fields.Int()
    type = fields.Constant("doctor")
    
    # 假设问诊标题使用病人的主诉症状
    title = fields.Str(attribute="patient_symptoms") 
    
    # 日期和时间使用预约时间
    date = fields.DateTime(attribute="appointment_time", format="%Y-%m-%d")
    time = fields.DateTime(attribute="appointment_time", format="%H:%M")
    
    status = fields.Str()
    
    # 摘要使用医生的诊断建议
    summary = fields.Str(attribute="doctor_diagnosis")
    
    # --- 医生问诊特有的字段 ---
    department = fields.Str()
    
    # "doctor" 字段需要从关联的 Doctor 对象中获取姓名
    # attribute="doctor.full_name" 会自动访问 DoctorConsultationModel.doctor 关系，
    # 然后再获取关联的 UserModel 上的 full_name 属性。
    doctor = fields.Str(attribute="doctor.full_name")