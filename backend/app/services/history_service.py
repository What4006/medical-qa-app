#9.23——用于  获取最近问诊记录  的API--w4006
from ..models.consultation_model import AIConsultationModel, DoctorConsultationModel, ChatMessageModel
from ..core.extensions import db
from ..models.medical_record_model import MedicalRecordModel
from ..services import llm_service
from ..models.user_model import UserModel
import json
from datetime import datetime
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
    main_consultation = AIConsultationModel.query.filter_by(patient_id=user_id).order_by(AIConsultationModel.created_at.desc()).first()
    
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

def get_chat_history(user_id):
    """
    获取指定用户所有AI问诊的聊天记录，并按文档要求配对成问答形式。
    不同会话之间会用一个特殊标记隔开。
    """
    # 1. 关联查询，获取该用户所有的聊天记录
    messages = db.session.query(ChatMessageModel).join(
        AIConsultationModel, AIConsultationModel.id == ChatMessageModel.consultation_id
    ).filter(
        AIConsultationModel.patient_id == user_id
    ).order_by(ChatMessageModel.timestamp).all() # 按时间排序

    chat_pairs = []
    i = 0
    last_consultation_id = None

    # 2. 遍历所有消息
    while i < len(messages):
        current_consultation_id = messages[i].consultation_id
        
        # 3. 如果这是一个新会话的开始，并且不是第一条消息，则插入一个分隔标记
        if last_consultation_id is not None and current_consultation_id != last_consultation_id:
            chat_pairs.append({"type": "separator"})
        
        last_consultation_id = current_consultation_id

        # 4. 配对问答逻辑保持不变
        if messages[i].sender_type == 'user':
            question = messages[i].content
            answer = "" # 默认答案为空
            
            # 查找紧随其后的那条是不是同一会话中AI的回答
            if (i + 1) < len(messages) and \
               messages[i+1].sender_type == 'ai' and \
               messages[i+1].consultation_id == current_consultation_id:
                answer = messages[i+1].content
                i += 1 # 如果是，则跳过下一条AI消息，因为已经配对
            
            chat_pairs.append({
                "question": question,
                "answer": answer,
                "createdAt": messages[i].timestamp.isoformat() + "Z"
            })
        i += 1
        
    return chat_pairs

#1.用户首次使用或无记录时被调用 2.通过特定 API 直接调用时: POST /api/history/create
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
    #-----------------------------------------------
    #这里应当增加一个更新AIConsultationModel实例的功能

    # 1. 更新摘要 (ai_analysis)：使用最新的AI回答作为问诊摘要
    consultation.ai_analysis = answer
    
    # 2. 更新诊断/标题 (ai_diagnosis)：使用最新的用户问题作为简短标题/诊断
    consultation.ai_diagnosis = question[:50] 
    
    # 3. 追加症状描述 (symptom_description)：将新问题追加到症状描述中
    if consultation.symptom_description:
        consultation.symptom_description += f"\n\n[User]: {question}"
    else:
        consultation.symptom_description = f"[User]: {question}"
        
    # 4. 更新状态 (status)：确保状态为 'completed' (表示此轮问答已完成)
    consultation.status = 'completed'

    #-----------------------------------------------
    # 3. 将新记录添加到数据库并提交
    db.session.add_all([user_message, ai_message])
    db.session.commit()
    
    # 返回主问诊对象，表示追加成功
    return consultation

def start_new_chat_session(user_id):
    """
    为用户开启一个新的对话会话。
    在我们的逻辑里，这意味着创建一个新的`AIConsultationModel`实例作为新会话的容器。
    """
    new_consultation = AIConsultationModel(
        patient_id=user_id,
        status='processing', # 标记为“进行中”
        ai_diagnosis=f"用户 {user_id} 的新AI对话", # 设置一个默认标题
        ai_analysis="这是一个新的AI问诊会话"
    )
    db.session.add(new_consultation)
    db.session.commit()
    # 返回新会话的ID，符合文档要求
    return f"chat_{new_consultation.id}"


def generate_medical_record_from_history(user_id):
    """
    根据用户的 patient_name 调用 LLM 服务生成结构化电子病历。
    (已修改为调用 llm_service.py)
    """
    
    # --- 1. (新增) 获取 patient_name ---
    # 你的 llm_service.py (llm_service.py) 需要 patient_name
    user = UserModel.query.get(user_id)
    if not user:
        print(f"Error in history_service: User not found for ID {user_id}")
        return None
    
    patient_name = user.full_name
    if not patient_name:
        print(f"Error in history_service: User {user_id} does not have a full_name set.")
        # FastAPI (Fastapi.txt) 明确要求 patient_name
        return None

    # --- 2. (修改) 调用 llm_service ---
    try:
        # 调用 llm_service.py (llm_service.py) 中你写好的函数
        print(f"--- Calling llm_service.generate_structured_medical_record for {patient_name} ---")
        generated_record_dict = llm_service.generate_structured_medical_record(patient_name)
    
    except Exception as e:
        # 捕获 llm_service (llm_service.py) 抛出的异常 (例如连接失败或FastAPI返回错误)
        print(f"Error calling llm_service for user {user_id} ({patient_name}): {e}")
        return None # 返回 None 表示生成失败

    if not generated_record_dict or "patient_name" not in generated_record_dict:
        print(f"Error: llm_service did not return a valid record dictionary.")
        return None

    # --- 3. (关键修改) 组合数据并保存到 Flask 数据库 ---
    try:
        # 从 AI (FastAPI) (Fastapi.txt) 获取动态信息
        ai_summary = generated_record_dict.get("summary", "暂无主诉")
        ai_encounters = generated_record_dict.get("encounters", [])
        
        # 从 encounters 提取简单的诊断
        primary_diagnosis = "暂无诊断"
        history_present_illness = "暂无现病史"
        
        if ai_encounters:
            first_encounter = ai_encounters[0]
            primary_diagnosis = first_encounter.get("diagnosis", "暂无诊断")
            history_present_illness = json.dumps(ai_encounters, ensure_ascii=False)

        # --- 替换占位符 ---
        new_medical_record = MedicalRecordModel(
            patient_id=user_id, 
            
            # 1. AI 生成的动态信息
            chief_complaint=ai_summary, # 使用FastAPI的summary
            history_present_illness=history_present_illness, # 存储 encounters 详情
            diagnosis=primary_diagnosis, # 使用第一个 encounter 的诊断
            
            # 2. 从 UserModel 提取的静态信息
            past_medical_history=user.basic_medical_history or "患者未提供", 
            personal_history=user.personal_history or "患者未提供", 
            family_history=user.family_history or "患者未提供"
        )
        
        db.session.add(new_medical_record)
        db.session.commit()
        
        # --- 4. (修改) 返回符合 API 文档 (大创文档xin.docx) 的字典 ---
        # [cite_start]你的Flask API (大创文档xin.docx) 需要返回中文键 [cite: 532]
        final_record_dict = {
            "id": str(new_medical_record.id),
            "主诉": new_medical_record.chief_complaint,
            "现病史": new_medical_record.history_present_illness,
            "既往史": new_medical_record.past_medical_history,
            "个人史": new_medical_record.personal_history,
            "家族史": new_medical_record.family_history,
            "诊断": new_medical_record.diagnosis,
            "createdAt": new_medical_record.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        return final_record_dict

    except Exception as e:
        db.session.rollback() # 保存失败时回滚
        print(f"Error saving medical record to Flask DB for user {user_id}: {e}")
        return None # 返回 None 表示保存失败