# backend/app/services/llm_service.py

import requests
import asyncio
import websockets
import json
import os
import threading # 导入 threading

# --- 配置 ---
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8000")

# --- 结构化服务 API 调用 ---
def generate_structured_medical_record(patient_name: str) -> dict:
    # ... (此函数保持不变) ...
    api_url = f"{FASTAPI_BASE_URL}/api/v1/medical_record/generate"
    payload = {"patient_name": patient_name}
    headers = {"Content-Type": "application/json"}
    try:
        print(f"--- 正在调用FastAPI：为 {patient_name} 生成病历 ---")
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        response_data = response.json()
        
        print(f"--- 收到FastAPI响应 (生成病历) ---")
        
        if "error" in response_data:
            print(f"FastAPI返回错误: {response_data.get('error')}")
            raise ValueError(f"FastAPI 错误: {response_data.get('error')}. 原始输出: {response_data.get('raw_output')}")
        
        if "patient_name" in response_data and "summary" in response_data and "encounters" in response_data:
             return response_data
        else:
             print("错误：FastAPI 为病历返回了意外的JSON结构。")
             raise ValueError("FastAPI 为病历返回了意外的JSON结构。")
             
    except requests.exceptions.RequestException as e:
        print(f"调用FastAPI generate_medical_record API时出错: {e}")
        raise ConnectionError(f"无法连接到FastAPI服务 {api_url}: {e}")
    except ValueError as e:
         print(f"处理FastAPI响应时出错: {e}")
         raise e
    except Exception as e:
         print(f"generate_structured_medical_record 中发生意外错误: {e}")
         raise RuntimeError(f"意外错误: {e}")


# --- 动态代理 API 调用 (WebSocket) ---
async def get_dynamic_response_async(question: str) -> str:
    # ... (此异步函数保持不变) ...
    start_api_url = f"{FASTAPI_BASE_URL}/api/v1/chat/start"
    payload = {"question": question}
    headers = {"Content-Type": "application/json"}
    session_id = None
    final_answer = "未能获取到有效的 AI 回答。"
    all_messages = []
    ws_url = "" # 初始化 ws_url

    try:
        print(f"--- Calling FastAPI: Starting chat session for question: {question[:50]}... ---")
        response = requests.post(start_api_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        session_id = response.json().get("session_id")
        print(f"--- FastAPI Session Started: {session_id} ---")
        if not session_id:
            raise ValueError("Failed to get session_id from FastAPI")

        # --- 构造 WebSocket URL (处理 https/wss) ---
        if FASTAPI_BASE_URL.startswith("https://"):
            domain_part = FASTAPI_BASE_URL.replace("https://", "", 1)
            ws_protocol = "wss"
        else:
            domain_part = FASTAPI_BASE_URL.replace("http://", "", 1)
            ws_protocol = "ws"
        ws_url = f"{ws_protocol}://{domain_part}/api/v1/chat/ws/{session_id}"
        #------------------------------------

        print(f"--- Connecting to WebSocket: {ws_url} ---")
        async with websockets.connect(ws_url, timeout=60) as websocket:
            print("--- WebSocket Connected ---")
            while True:
                try:
                    message_str = await asyncio.wait_for(websocket.recv(), timeout=120)
                    message = json.loads(message_str)
                    message_type = message.get("type")
                    print(f"Received WS Message: Type={message_type}, Speaker={message.get('speaker', 'N/A')}")
                    if message_type == "agent_message":
                        content = message.get("content", "")
                        speaker = message.get("speaker", "")
                        all_messages.append(f"{speaker}: {content}")
                        if speaker == "Summarizer_Agent":
                             final_answer = content
                             print("--- Final answer identified from Summarizer_Agent ---")
                    elif message_type == "error":
                        error_content = message.get("content", "Unknown error")
                        print(f"Error from WebSocket: {error_content}")
                        final_answer = f"处理过程中发生错误: {error_content}"
                        break
                    elif message_type == "session_end":
                        print("--- WebSocket Session Ended signal received ---")
                        if final_answer == "未能获取到有效的 AI 回答." and all_messages:
                            final_answer = "\n".join(all_messages)
                        break
                    else:
                        print(f"Received unknown message type: {message_type}")
                except asyncio.TimeoutError:
                    print("WebSocket receive timeout.")
                    final_answer = "等待 AI 响应超时。"
                    break
                except websockets.exceptions.ConnectionClosedOK:
                    print("WebSocket connection closed normally.")
                    break
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"WebSocket connection closed with error: {e}")
                    final_answer = "与 AI 服务连接中断。"
                    break
                except Exception as e:
                    print(f"Error processing WebSocket message: {e}")
                    final_answer = f"处理 AI 消息时出错: {e}"
                    break
    except requests.exceptions.RequestException as e:
        print(f"Error calling FastAPI start_chat API: {e}")
        final_answer = f"无法连接到 AI 服务: {e}"
    except websockets.exceptions.InvalidURI:
         print(f"Invalid WebSocket URI: {ws_url}")
         final_answer = "配置的 AI 服务地址无效。"
    except websockets.exceptions.WebSocketException as e:
         print(f"WebSocket connection failed: {e}")
         final_answer = f"无法建立与 AI 服务的实时连接: {e}"
    except ValueError as e:
        print(f"Data error: {e}")
        final_answer = f"AI 服务返回数据错误: {e}"
    except Exception as e:
        print(f"An unexpected error occurred in get_dynamic_response_async: {e}")
        final_answer = f"发生意外错误: {e}"
    print(f"--- Dynamic Response Function Returning: {final_answer[:100]}... ---")
    return final_answer


# --- 同步包装器 (修改后) ---
def _run_async_in_thread(coro):
    """辅助函数：在一个新事件循环中运行协程"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def get_dynamic_response(question: str) -> str:
    """
    同步调用 get_dynamic_response_async。
    处理在 Flask 线程中运行 asyncio 的问题。
    """
    current_thread = threading.current_thread()
    print(f"--- get_dynamic_response called in thread: {current_thread.name} ({current_thread.ident}) ---")
    try:
        # 尝试直接使用 asyncio.run()，这是最简洁的方式，但在某些线程环境下可能失败
        # 注意：asyncio.run() 会自动创建和管理事件循环
        return asyncio.run(get_dynamic_response_async(question))
    except RuntimeError as e:
        # 捕获 asyncio.run() 可能抛出的 RuntimeError
        print(f"asyncio.run() failed: {e}. Trying to run in a new event loop.")
        # 如果 asyncio.run() 失败（比如因为当前线程已有循环但未运行，或明确无循环）
        # 则尝试在一个新的、专用的事件循环中运行异步代码
        try:
            # 使用辅助函数在新循环中运行
            return _run_async_in_thread(get_dynamic_response_async(question))
        except Exception as inner_e:
            print(f"Running async in new loop failed: {inner_e}")
            return f"执行异步 AI 请求失败: {inner_e}"
    except Exception as e:
        # 捕获其他可能的异常
        print(f"Error in get_dynamic_response wrapper: {e}")
        return f"调用 AI 服务时发生错误: {e}"


# --- 替换旧的模拟函数 ---
def get_ai_response(question: str) -> str:
    """
    获取 AI 对医疗问题的回答。
    现在调用新的动态代理 API。
    """
    return get_dynamic_response(question)

