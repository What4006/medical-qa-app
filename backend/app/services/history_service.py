#9.23——用于  获取最近问诊记录  的API--w4006
from ..models.consultation_model import AIConsultationModel, DoctorConsultationModel, ChatMessageModel
from ..core.extensions import db

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
    
def get_all_consulations(user_id):
    ai_records=AIConsultationModel.query.filter_by(patient_id=user_id).all()
    doctor_records=DoctorConsultationModel.query.filter_by(patient_id=user_id).all()
    return ai_records,doctor_records

def find_or_create_main_ai_consultation(user_id):
    """
    为指定用户查找其唯一的AI问诊主记录。如果不存在，则创建一个。
    返回主问诊记录对象。
    """
    # 1. 尝试根据 patient_id 查找已存在的AI问诊记录
    main_consultation = AIConsultationModel.query.filter_by(patient_id=user_id).first()
    
    # 2. 如果找到了，直接返回
    if main_consultation:
        return main_consultation
        
    # 3. 如果没找到，为该用户创建一个全新的主问诊记录
    else:
        # 准备一条初始的、虚拟的问答对，作为“欢迎消息”
        initial_question = "开始新的问诊"
        initial_answer = "您好！我是AI问诊助手，很高兴为您服务。请描述您的症状..."

        # 调用您指定的、更完整的创建函数
        new_consultation = create_ai_consultation_record(user_id, initial_question, initial_answer)
        
        return new_consultation

def get_chat_history(user_id, consultation_id):
    """
    获取指定AI问诊的所有聊天记录，并按文档要求配对成问答形式。
    """
    # 关联查询 AIConsultationModel 以确保用户只能访问自己的记录
    messages = db.session.query(ChatMessageModel).join(
        AIConsultationModel, AIConsultationModel.id == ChatMessageModel.consultation_id
    ).filter(
        AIConsultationModel.patient_id == user_id,
        AIConsultationModel.id == consultation_id
    ).order_by(ChatMessageModel.timestamp).all()

    chat_pairs = []
    i = 0
    # 遍历所有消息
    while i < len(messages):
        # 找到一个用户提问
        if messages[i].sender_type == 'user':
            question = messages[i].content
            answer = "" # 默认答案为空
            
            # 查找紧随其后的那条是不是AI的回答
            if (i + 1) < len(messages) and messages[i+1].sender_type == 'ai':
                answer = messages[i+1].content
                i += 1 # 如果是，则跳过下一条AI消息，因为已经配对
            
            # 按照文档格式组合
            chat_pairs.append({
                "question": question,
                "answer": answer,
                "createdAt": messages[i].timestamp.isoformat() + "Z"
            })
        i += 1
        
    return chat_pairs

def create_ai_consultation_record(user_id, question, answer):
    """
    创建一个新的AI问诊记录，并保存第一条问答对。
    """
    # 1. 创建一个新的主问诊记录 (ai_consultations table)
    new_consultation = AIConsultationModel(
        patient_id=user_id,
        status='completed',  # 根据文档，AI问诊直接是已完成
        ai_diagnosis=question[:50],  # 使用问题的前50个字符作为临时标题
        ai_analysis=answer  # 问诊摘要就是AI的回答
    )
    db.session.add(new_consultation)
    # 需要先 flush 来获取 new_consultation 的数据库自增 id
    db.session.flush()

    # 2. 创建用户提问的消息记录 (chat_messages table)
    user_message = ChatMessageModel(
        consultation_id=new_consultation.id,
        sender_type='user',
        content=question
    )
    # 3. 创建AI回答的消息记录 (chat_messages table)
    ai_message = ChatMessageModel(
        consultation_id=new_consultation.id,
        sender_type='ai',
        content=answer
    )
    
    db.session.add_all([user_message, ai_message])
    db.session.commit()
    
    # 返回创建好的主问诊对象，方便API层使用
    return new_consultation

def add_chat_message_to_consultation(user_id, consultation_id, question, answer):
    """
    向一个已存在的AI问诊中追加一条问答记录。
    """
    # 1. 验证这次问诊是否真实存在且属于当前登录的用户
    consultation = AIConsultationModel.query.filter_by(id=consultation_id, patient_id=user_id).first()
    
    # 如果找不到，说明 consultation_id 无效或用户无权访问
    if not consultation:
        return None  # 返回 None 表示操作失败

    # 2. 创建用户提问和AI回答的两条新聊天记录
    user_message = ChatMessageModel(
        consultation_id=consultation.id,
        sender_type='user',
        content=question
    )
    ai_message = ChatMessageModel(
        consultation_id=consultation.id,
        sender_type='ai',
        content=answer
    )
    
    # 3. 将新记录添加到数据库并提交
    db.session.add_all([user_message, ai_message])
    db.session.commit()
    
    # 返回主问诊对象，表示追加成功
    return consultation