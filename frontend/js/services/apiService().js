// 后端API基础地址（根据实际部署环境修改）
const API_BASE_URL = 'http://localhost:5000/api';

/**
 * 辅助函数：获取认证请求头
 * @returns {Object} 包含认证信息的请求头配置
 * @throws {Error} 当没有找到有效的token时抛出错误
 */
function getAuthHeaders() {
  // 从localStorage获取登录时保存的token
  const token = localStorage.getItem('access_token');
  
  // 验证token是否存在
  if (!token) {
    throw new Error('用户未登录或token已过期');
  }
  
  // 返回包含认证信息的请求头
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}` // JWT认证格式
  };
}

const apiService = {
  /**
   * 获取当前登录用户信息
   * 对应后端需要JWT认证的接口：GET /api/user/current
   */
  getCurrentUser: async function() {
    try {
      const response = await fetch(`${API_BASE_URL}/user/current`, {
        method: 'GET',
        headers: getAuthHeaders(), // 使用认证头
        credentials: 'include'
      });

      // 先解析响应数据
      const data = await response.json();

      // 处理401未授权错误（用户未登录）
      if (response.status === 401) {
        // 清除无效token
        localStorage.removeItem('access_token');
        // 使用接口返回的错误信息，如果没有则使用默认信息
        throw new Error(data.message || '用户未登录');
      }

      if (!response.ok) {
        throw new Error(`获取用户信息失败: ${data.message || response.statusText}`);
      }

      // 直接返回用户信息对象（根据文档，成功响应直接是用户信息对象）
      return data;
    } catch (error) {
      console.error('getCurrentUser API调用失败:', error.message);
      throw error;
    }
  },

  /**
   * 获取最近一条问诊记录（需要认证）
   * 对应后端接口：GET /api/history/recent
   * @returns {Promise<Object|null>} 最近一条问诊记录对象，无记录时返回null
   */
  getRecentMedicalRecord: async function() {
    try {
      // 发起带认证的GET请求，使用新的接口路径
      const response = await fetch(`${API_BASE_URL}/history/recent`, {
        method: 'GET',
        headers: getAuthHeaders(), // 使用认证头
        credentials: 'include'
      });

      // 处理401未授权错误
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('登录已过期，请重新登录');
      }

      // 处理500服务器错误
      if (response.status === 500) {
        const errorData = await response.json();
        throw new Error(errorData.message || '服务器内部错误');
      }

      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
      }

      // 根据API文档，无记录时返回null，有记录时返回对象
      const record = await response.json();
      
      // 验证返回数据格式
      if (record !== null && (typeof record !== 'object' || Array.isArray(record))) {
        throw new Error('后端返回数据格式错误：应为对象或null');
      }

      return record;

    } catch (error) {
      console.error('getRecentMedicalRecord API调用失败:', error.message);
      throw error;
    }
  },

  /**
   * 获取全部问诊记录（需要认证，无分页）
   * 对应后端接口：GET /api/history/all
   * @returns {Promise<Array>} 所有问诊记录组成的数组
   */
  getAllMedicalRecords: async function() {
    try {
      // 直接使用基础URL，不添加分页参数
      const response = await fetch(`${API_BASE_URL}/history/all`, {
        method: 'GET',
        headers: getAuthHeaders(),
        credentials: 'include'
      });

      // 处理401未授权错误
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('登录已过期，请重新登录');
      }

      // 处理500服务器错误
      if (response.status === 500) {
        const errorData = await response.json();
        throw new Error(errorData.message || '服务器内部错误');
      }

      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
      }

      // 获取所有记录列表
      const records = await response.json();
      
      // 验证返回数据格式应为数组
      if (!Array.isArray(records)) {
        throw new Error('后端返回数据格式错误：应为数组');
      }

      return records;

    } catch (error) {
      console.error('getAllMedicalRecords API调用失败:', error.message);
      throw error;
    }
  },
  
  /**
   * 发送医疗问题到AI模型，获取诊断建议
   * 后端接口：POST /api/chat/medical
   * @param {string} question 用户的问题
   * @returns {Promise<string>} AI返回的诊断建议
   */
  sendMedicalQuery: async function(question) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/medical`, {
        method: 'POST',
        headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        credentials: 'include'
      });

      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('登录已过期，请重新登录');
      }
      if (response.status === 500) {
        const errorData = await response.json();
        throw new Error(errorData.message || '服务器内部错误');
      }
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`请求失败: ${errorData.message || response.statusText}`);
      }

      const data = await response.json();
      return data.answer; // 假设后端返回 { "answer": "AI回答内容" }
    } catch (error) {
      console.error('sendMedicalQuery 调用失败:', error.message);
      throw error;
    }
  },

  /**
   * 发送医疗问题和文件到AI模型，获取诊断建议
   * 后端接口：POST /api/chat/medical/upload
   * @param {string} question 用户的问题
   * @param {Array<File>} files 文件数组
   * @returns {Promise<string>} AI返回的诊断建议
   */
  sendMedicalQueryWithFiles: async function(question, files) {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('用户未登录或token已过期');
      const formData = new FormData();
      formData.append('question', question);
      files.forEach(f => formData.append('files', f));
      const response = await fetch(`${API_BASE_URL}/chat/medical/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
        credentials: 'include'
      });
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('登录已过期，请重新登录');
      }
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || response.statusText);
      }
      const data = await response.json();
      return data.answer;
    } catch (error) {
      console.error('sendMedicalQueryWithFiles 调用失败:', error.message);
      throw error;
    }
  },

  /**
   * 创建医疗问诊历史记录
   * 后端接口：POST /api/history/create
   * @param {string} question 用户问题
   * @param {string} answer AI回答
   * @returns {Promise<Object>} 保存的历史记录对象
   */
  createMedicalRecord: async function(question, answer) {
    try {
      const response = await fetch(`${API_BASE_URL}/history/create`, {
        method: 'POST',
        headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'ai',        // 标记为AI问诊
          title: 'AI问诊记录',
          summary: `用户问题：${question}\nAI回答：${answer}`,
          question,
          answer
        }),
        credentials: 'include'
      });

      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('登录已过期，请重新登录');
      }
      if (response.status === 500) {
        const errorData = await response.json();
        throw new Error(errorData.message || '服务器内部错误');
      }
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`创建记录失败: ${errorData.message || response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('createMedicalRecord 调用失败:', error.message);
      throw error;
    }
  },

  /**
   * 获取AI问诊历史对话记录
   * 后端接口：GET /api/chat/history
   * @returns {Promise<Array>} 历史对话数组，格式为 [{question: "用户问题", answer: "AI回答", createdAt: "时间戳"}, ...]
   */
  getMedicalChatHistory: async function() {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/history`, {
        method: 'GET',
        headers: getAuthHeaders(),
        credentials: 'include'
      });

      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error('登录已过期，请重新登录');
      }
      if (response.status === 500) {
        const errorData = await response.json();
        throw new Error(errorData.message || '服务器内部错误');
      }
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`获取历史记录失败: ${errorData.message || response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('getMedicalChatHistory 调用失败:', error.message);
      throw error;
    }
  },
  //---------------------------------------新增-------------------------------------
  /**
   * 通知后端开启一个新对话
   * 对应后端接口: POST /api/chat/new
   * @returns {Promise<Object>} 成功时返回 { success: true, message: "...", chatId: "..." }
   */
  startNewMedicalChat: async function() {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/new`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include'
      });

      const data = await response.json();

      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error(data.message || '用户未登录');
      }
      if (!response.ok) {
        throw new Error(data.message || '无法创建新对话');
      }
      return data;
    } catch (error) {
      console.error('startNewMedicalChat API调用失败:', error.message);
      throw error;
    }
  },

  /**
   * 请求后端根据历史记录生成病历
   * 对应后端接口: POST /api/chat/medical/record
   * @returns {Promise<Object>} 返回结构化的病历对象
   */
  generateMedicalRecord: async function() {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/medical/record`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include'
      });

      const data = await response.json();

      if (response.status === 401) {
        localStorage.removeItem('access_token');
        throw new Error(data.message || '用户未登录');
      }
      if (response.status === 404) {
        throw new Error(data.message || '无足够的问诊记录生成病历');
      }
      if (!response.ok) {
        throw new Error(data.message || '生成病历失败');
      }
      return data;
    } catch (error) {
      console.error('generateMedicalRecord API调用失败:', error.message);
      throw error;
    }
  },
  // 其他需要认证的API方法...
};
//export default apiService;