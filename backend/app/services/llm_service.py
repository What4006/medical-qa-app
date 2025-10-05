 # 封装与大模型交互的逻辑

#测试模拟
# backend/app/services/llm_service.py
def get_ai_response(question: str) -> str:
    """
    【模拟】的AI模型服务。
    """
    print(f"--- MOCK AI SERVICE ---")
    print(f"收到问题: {question}")
    # ...
    response_text = f"这是一个针对您的问题 '{question}' 的模拟AI回答。"
    return response_text