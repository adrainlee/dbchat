import React, { createContext, useContext, useState, useEffect } from 'react';
import { databaseApi, aiApi, historyApi } from '../services/api';

// 创建AppContext
const AppContext = createContext();

// 创建自定义hook，方便组件使用context
export const useAppContext = () => useContext(AppContext);

// AppProvider组件，用于提供全局状态
export const AppProvider = ({ children }) => {
  // 数据库连接状态
  const [isDatabaseConnected, setIsDatabaseConnected] = useState(false);
  const [databaseSchema, setDatabaseSchema] = useState(null);
  const [databaseType, setDatabaseType] = useState('');
  
  // AI连接状态
  const [aiConnections, setAiConnections] = useState([]);
  const [selectedConnection, setSelectedConnection] = useState(null);
  
  // 查询历史状态
  const [historyItems, setHistoryItems] = useState([]);
  
  // 全局错误和消息状态
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // 加载状态
  const [isLoading, setIsLoading] = useState(false);
  
  // 初始加载数据
  useEffect(() => {
    // 检查数据库连接状态
    const checkDatabaseConnection = async () => {
      try {
        const schema = await databaseApi.getDatabaseSchema();
        setDatabaseSchema(schema);
        setIsDatabaseConnected(true);
        // 我们可以在这里尝试获取数据库类型
      } catch (error) {
        console.log('数据库未连接或发生错误');
        setIsDatabaseConnected(false);
      }
    };
    
    // 加载AI连接
    const loadAiConnections = async () => {
      try {
        const connections = await aiApi.getAiConnections();
        setAiConnections(connections);
        if (connections.length > 0) {
          setSelectedConnection(connections[0]);
        }
      } catch (error) {
        console.error('获取AI连接错误:', error);
        setError('无法加载AI连接配置');
      }
    };
    
    checkDatabaseConnection();
    loadAiConnections();
  }, []);
  
  // 连接到数据库
  const connectToDatabase = async (connectionString) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await databaseApi.connectToDatabase(connectionString);
      const schema = await databaseApi.getDatabaseSchema();
      setDatabaseSchema(schema);
      setIsDatabaseConnected(true);
      setSuccessMessage('成功连接到数据库');
      return true;
    } catch (error) {
      setError(`连接数据库错误: ${error.message}`);
      return false;
    } finally {
      setIsLoading(false);
    }
  };
  
  // 执行AI查询
  const executeAiQuery = async (prompt) => {
    if (!selectedConnection) {
      setError('请先选择AI连接');
      return null;
    }
    
    if (!isDatabaseConnected) {
      setError('请先连接到数据库');
      return null;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await aiApi.generateSqlQuery(
        prompt,
        selectedConnection.model_name,
        selectedConnection.service_type
      );
      
      // 更新历史记录
      const historyItem = {
        id: Date.now(), // 临时ID
        timestamp: new Date(),
        prompt,
        query: response.query,
        summary: response.summary
      };
      
      // 添加到历史记录
      try {
        await historyApi.addHistoryItem(historyItem);
        setHistoryItems([historyItem, ...historyItems]);
      } catch (historyError) {
        console.error('保存历史记录错误:', historyError);
      }
      
      return response;
    } catch (error) {
      setError(`生成查询错误: ${error.message}`);
      return null;
    } finally {
      setIsLoading(false);
    }
  };
  
  // 执行SQL查询
  const executeSqlQuery = async (query) => {
    if (!isDatabaseConnected) {
      setError('请先连接到数据库');
      return null;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const results = await databaseApi.executeQuery(query);
      return results;
    } catch (error) {
      setError(`执行查询错误: ${error.message}`);
      return null;
    } finally {
      setIsLoading(false);
    }
  };
  
  // 清除错误消息
  const clearError = () => {
    setError(null);
  };
  
  // 清除成功消息
  const clearSuccessMessage = () => {
    setSuccessMessage(null);
  };
  
  // 更新选择的AI连接
  const updateSelectedConnection = (connectionId) => {
    const connection = aiConnections.find(conn => conn.id === connectionId);
    if (connection) {
      setSelectedConnection(connection);
    }
  };
  
  // 提供给context的值
  const contextValue = {
    // 状态
    isDatabaseConnected,
    databaseSchema,
    databaseType,
    aiConnections,
    selectedConnection,
    historyItems,
    error,
    successMessage,
    isLoading,
    
    // 操作方法
    connectToDatabase,
    executeAiQuery,
    executeSqlQuery,
    clearError,
    clearSuccessMessage,
    updateSelectedConnection,
    setError,
    setSuccessMessage,
    setAiConnections,
    setHistoryItems
  };
  
  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContext;