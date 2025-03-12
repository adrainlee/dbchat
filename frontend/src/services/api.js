import axios from 'axios';

// 创建axios实例，设置基础URL
const api = axios.create({
  baseURL: '/api', // 使用相对路径，会通过package.json中的proxy配置转发到后端
  timeout: 30000, // 超时时间设置为30秒
  headers: {
    'Content-Type': 'application/json',
  },
});

// 数据库相关API
export const databaseApi = {
  // 连接到数据库
  connectToDatabase: (connectionString) => {
    return api.post('/database/connect', null, { params: { connection_string: connectionString } });
  },
  
  // 测试数据库连接
  testConnection: (connectionString) => {
    return api.post('/database/test', null, { params: { connection_string: connectionString } });
  },
  
  // 获取数据库架构
  getDatabaseSchema: () => {
    return api.get('/database/schema');
  },
  
  // 执行SQL查询
  executeQuery: (query) => {
    return api.post('/database/execute', null, { params: { query } });
  }
};

// AI相关API
export const aiApi = {
  // 生成SQL查询
  generateSqlQuery: (prompt, aiModel, aiService) => {
    return api.post('/ai/query', {
      prompt,
      ai_model: aiModel,
      ai_service: aiService
    });
  },
  
  // 与AI对话
  chatWithAi: (messages, aiModel, aiService) => {
    return api.post('/ai/chat', {
      messages,
      ai_model: aiModel,
      ai_service: aiService
    });
  },
  
  // 获取AI连接配置
  getAiConnections: () => {
    return api.get('/ai/connections');
  }
};

// 历史记录相关API
export const historyApi = {
  // 获取历史记录
  getHistoryItems: () => {
    return api.get('/history');
  },
  
  // 添加历史记录
  addHistoryItem: (item) => {
    return api.post('/history', item);
  },
  
  // 删除历史记录
  deleteHistoryItem: (id) => {
    return api.delete(`/history/${id}`);
  },
  
  // 清空历史记录
  clearHistory: () => {
    return api.delete('/history');
  }
};

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 这里可以添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    let message = '未知错误';
    if (error.response) {
      // 服务器返回错误
      message = error.response.data.detail || error.response.data.message || `错误: ${error.response.status}`;
    } else if (error.request) {
      // 请求未收到响应
      message = '服务器未响应';
    } else {
      // 请求配置出错
      message = error.message;
    }
    
    console.error('API错误:', message);
    return Promise.reject(new Error(message));
  }
);

export default api;