import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
} from '@mui/material';

import { databaseApi } from '../services/api';
import { useAppContext } from '../context/AppContext';

const ConnectDb = () => {
  // 导航
  const navigate = useNavigate();
  
  // 使用全局状态
  const { 
    connectToDatabase, 
    setError, 
    setSuccessMessage, 
    isLoading 
  } = useAppContext();
  
  // 本地状态变量
  const [connectionString, setConnectionString] = useState('');
  const [databaseType, setDatabaseType] = useState('mysql');
  const [isTesting, setIsTesting] = useState(false);
  const [localError, setLocalError] = useState(null);
  const [localSuccess, setLocalSuccess] = useState(null);
  
  // 构建连接字符串模板
  const getConnectionTemplate = () => {
    switch (databaseType) {
      case 'mysql':
        return 'mysql://user:password@localhost:3306/database';
      case 'postgres':
        return 'postgresql://user:password@localhost:5432/database';
      case 'sqlserver':
        return 'mssql://user:password@localhost:1433/database';
      default:
        return '';
    }
  };
  
  // 测试连接处理函数
  const handleTestConnection = async () => {
    if (!connectionString) {
      setError('请输入连接字符串');
      return;
    }
    
    setIsTesting(true);
    setLocalError(null);
    
    try {
      const response = await databaseApi.testConnection(connectionString);
      
      if (response.success) {
        setLocalSuccess('连接测试成功');
      } else {
        setLocalError('连接测试失败');
      }
    } catch (error) {
      setLocalError(`连接测试错误`);
      console.error(error);
    } finally {
      setIsTesting(false);
    }
  };
  
  // 连接数据库处理函数
  const handleConnect = async () => {
    if (!connectionString) {
      setError('请输入连接字符串');
      return;
    }
    
    try {
      // 使用全局方法连接数据库
      const success = await connectToDatabase(connectionString);
      
      if (success) {
        setSuccessMessage('数据库连接成功');
        
        // 连接成功后延迟导航到首页
        setTimeout(() => {
          navigate('/');
        }, 1500);
      }
    } catch (error) {
      // 错误已在全局状态中处理
      console.error(error);
    }
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        连接到数据库
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel id="database-type-label">数据库类型</InputLabel>
              <Select
                labelId="database-type-label"
                value={databaseType}
                label="数据库类型"
                onChange={(e) => setDatabaseType(e.target.value)}
              >
                <MenuItem value="mysql">MySQL</MenuItem>
                <MenuItem value="postgres">PostgreSQL</MenuItem>
                <MenuItem value="sqlserver">SQL Server</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="连接字符串"
              value={connectionString}
              onChange={(e) => setConnectionString(e.target.value)}
              placeholder={getConnectionTemplate()}
              variant="outlined"
              helperText={`示例: ${getConnectionTemplate()}`}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between">
              <Button
                variant="outlined"
                onClick={handleTestConnection}
                disabled={isTesting || !connectionString}
              >
                {isTesting ? (
                  <>
                    <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                    测试中...
                  </>
                ) : (
                  '测试连接'
                )}
              </Button>
              
              <Button
                variant="contained"
                color="primary"
                onClick={handleConnect}
                disabled={isLoading || !connectionString}
              >
                {isLoading ? (
                  <>
                    <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                    连接中...
                  </>
                ) : (
                  '连接数据库'
                )}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {localError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {localError}
        </Alert>
      )}
      
      {localSuccess && (
        <Alert 
          severity="success" 
          sx={{ mt: 2 }}
          onClose={() => setLocalSuccess(null)}
        >
          {localSuccess}
        </Alert>
      )}
      
      <Paper elevation={2} sx={{ p: 3, mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          连接帮助
        </Typography>
        
        <Typography variant="body2" paragraph>
          连接字符串格式取决于您使用的数据库类型:
        </Typography>
        
        <Typography variant="subtitle2">MySQL:</Typography>
        <Typography variant="body2" sx={{ ml: 2 }} paragraph>
          mysql://username:password@hostname:port/database
        </Typography>
        
        <Typography variant="subtitle2">PostgreSQL:</Typography>
        <Typography variant="body2" sx={{ ml: 2 }} paragraph>
          postgresql://username:password@hostname:port/database
        </Typography>
        
        <Typography variant="subtitle2">SQL Server:</Typography>
        <Typography variant="body2" sx={{ ml: 2 }} paragraph>
          mssql://username:password@hostname:port/database
        </Typography>
        
        <Alert severity="info" sx={{ mt: 2 }}>
          请确保您的数据库服务器允许远程连接，并且防火墙已配置允许连接到数据库端口。
        </Alert>
      </Paper>
    </div>
  );
};

export default ConnectDb;