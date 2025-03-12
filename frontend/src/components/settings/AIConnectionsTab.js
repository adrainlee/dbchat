import React, { useState, useEffect } from 'react';
import {
  Typography,
  Paper,
  Grid,
  Box,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

import { aiApi } from '../../services/api';

const AIConnectionsTab = ({ onError, onSuccess }) => {
  // AI连接状态
  const [aiConnections, setAiConnections] = useState([]);
  const [newConnectionDialog, setNewConnectionDialog] = useState(false);
  const [newConnection, setNewConnection] = useState({
    name: '',
    service_type: 'OpenAI',
    model_name: '',
    api_key: '',
    endpoint: '',
  });
  const [isAddingConnection, setIsAddingConnection] = useState(false);
  
  // 获取AI连接
  useEffect(() => {
    const fetchConnections = async () => {
      try {
        const connections = await aiApi.getAiConnections();
        setAiConnections(connections);
      } catch (error) {
        console.error('获取AI连接错误:', error);
        onError && onError('获取AI连接失败');
      }
    };
    
    fetchConnections();
  }, [onError]);
  
  // 打开添加连接对话框
  const handleOpenNewConnectionDialog = () => {
    setNewConnectionDialog(true);
  };
  
  // 关闭添加连接对话框
  const handleCloseNewConnectionDialog = () => {
    setNewConnectionDialog(false);
    setNewConnection({
      name: '',
      service_type: 'OpenAI',
      model_name: '',
      api_key: '',
      endpoint: '',
    });
  };
  
  // 添加新连接
  const handleAddConnection = async () => {
    // 验证输入
    if (!newConnection.name || !newConnection.model_name) {
      onError && onError('请填写所有必要的字段');
      return;
    }
    
    setIsAddingConnection(true);
    
    try {
      // 注意：在实际应用中，这里应该调用API添加连接
      // 由于我们的后端实现简化了这部分，这里只是模拟
      const newConnectionWithId = {
        ...newConnection,
        id: Date.now(), // 使用时间戳作为临时ID
      };
      
      setAiConnections([...aiConnections, newConnectionWithId]);
      onSuccess && onSuccess('成功添加AI连接');
      handleCloseNewConnectionDialog();
    } catch (error) {
      onError && onError(`添加连接错误: ${error.message}`);
    } finally {
      setIsAddingConnection(false);
    }
  };
  
  // 删除连接
  const handleDeleteConnection = async (connectionId) => {
    try {
      // 这里同样，在实际应用中应该调用API删除连接
      setAiConnections(aiConnections.filter(conn => conn.id !== connectionId));
      onSuccess && onSuccess('成功删除AI连接');
    } catch (error) {
      onError && onError(`删除连接错误: ${error.message}`);
    }
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">AI连接配置</Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenNewConnectionDialog}
          >
            添加连接
          </Button>
        </Box>
        
        {aiConnections.length === 0 ? (
          <Alert severity="info">
            没有配置的AI连接。点击"添加连接"按钮添加一个新的连接。
          </Alert>
        ) : (
          <Paper elevation={2}>
            <List>
              {aiConnections.map((connection, index) => (
                <React.Fragment key={connection.id}>
                  {index > 0 && <Divider />}
                  <ListItem
                    secondaryAction={
                      <IconButton
                        edge="end"
                        aria-label="删除"
                        onClick={() => handleDeleteConnection(connection.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <ListItemText
                      primary={connection.name}
                      secondary={`${connection.service_type} - ${connection.model_name}`}
                    />
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </Paper>
        )}
      </Grid>
      
      {/* 添加新连接对话框 */}
      <Dialog open={newConnectionDialog} onClose={handleCloseNewConnectionDialog} maxWidth="sm" fullWidth>
        <DialogTitle>添加新的AI连接</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="连接名称"
                value={newConnection.name}
                onChange={(e) => setNewConnection({ ...newConnection, name: e.target.value })}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>服务类型</InputLabel>
                <Select
                  value={newConnection.service_type}
                  label="服务类型"
                  onChange={(e) => setNewConnection({ ...newConnection, service_type: e.target.value })}
                >
                  <MenuItem value="OpenAI">OpenAI</MenuItem>
                  <MenuItem value="AzureOpenAI">Azure OpenAI</MenuItem>
                  <MenuItem value="Ollama">Ollama</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="模型名称"
                value={newConnection.model_name}
                onChange={(e) => setNewConnection({ ...newConnection, model_name: e.target.value })}
                placeholder={newConnection.service_type === 'OpenAI' ? 'gpt-4' : newConnection.service_type === 'AzureOpenAI' ? 'gpt-35-turbo' : 'llama2'}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API密钥"
                value={newConnection.api_key}
                onChange={(e) => setNewConnection({ ...newConnection, api_key: e.target.value })}
                type="password"
                required={newConnection.service_type !== 'Ollama'}
              />
            </Grid>
            
            {(newConnection.service_type === 'AzureOpenAI' || newConnection.service_type === 'Ollama') && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="端点"
                  value={newConnection.endpoint}
                  onChange={(e) => setNewConnection({ ...newConnection, endpoint: e.target.value })}
                  placeholder={newConnection.service_type === 'AzureOpenAI' ? 'https://your-resource.openai.azure.com' : 'http://localhost:11434'}
                  required
                />
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseNewConnectionDialog}>取消</Button>
          <Button 
            onClick={handleAddConnection} 
            variant="contained" 
            disabled={isAddingConnection}
          >
            {isAddingConnection ? '添加中...' : '添加'}
          </Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
};

export default AIConnectionsTab;