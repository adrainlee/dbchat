import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  TextField,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Grid,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Box,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

// 导入全局Context
import { useAppContext } from '../context/AppContext';

const Home = () => {
  // 导航
  const navigate = useNavigate();
  
  // 使用全局状态
  const {
    isDatabaseConnected,
    aiConnections,
    selectedConnection,
    isLoading,
    setError,
    executeAiQuery,
    executeSqlQuery,
    updateSelectedConnection
  } = useAppContext();
  
  // 本地状态
  const [userPrompt, setUserPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [queryResults, setQueryResults] = useState(null);
  const [localError, setLocalError] = useState(null);

  // 处理用户提示提交
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!userPrompt.trim()) {
      setError('请输入查询内容');
      return;
    }
    
    if (!isDatabaseConnected) {
      setError('请先连接到数据库');
      return;
    }
    
    if (!selectedConnection) {
      setError('请选择AI连接');
      return;
    }
    
    setIsGenerating(true);
    setLocalError(null);
    setAiResponse(null);
    setQueryResults(null);
    
    try {
      // 使用全局方法生成SQL查询
      const response = await executeAiQuery(userPrompt);
      
      if (response) {
        setAiResponse(response);
        
        // 执行生成的查询
        const results = await executeSqlQuery(response.query);
        if (results) {
          setQueryResults(results);
        }
      }
    } catch (error) {
      setLocalError(`处理查询时发生错误`);
    } finally {
      setIsGenerating(false);
    }
  };

  // 执行SQL查询
  const handleExecuteQuery = async (query) => {
    setIsExecuting(true);
    
    try {
      const results = await executeSqlQuery(query);
      if (results) {
        setQueryResults(results);
      }
    } catch (error) {
      setLocalError(`执行查询错误`);
    } finally {
      setIsExecuting(false);
    }
  };

  // 连接数据库按钮处理
  const handleConnectDatabase = () => {
    navigate('/connect');
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        数据库AI助手
      </Typography>
      
      {!isDatabaseConnected && (
        <Alert severity="warning" action={
          <Button color="inherit" size="small" onClick={handleConnectDatabase}>
            连接数据库
          </Button>
        }>
          您需要先连接到数据库才能使用查询功能
        </Alert>
      )}
      
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="ai-connection-label">AI模型</InputLabel>
                <Select
                  labelId="ai-connection-label"
                  value={selectedConnection ? selectedConnection.id : ''}
                  label="AI模型"
                  onChange={(e) => updateSelectedConnection(e.target.value)}
                  disabled={!aiConnections.length}
                >
                  {aiConnections.map((conn) => (
                    <MenuItem key={conn.id} value={conn.id}>
                      {conn.name} ({conn.service_type})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="用自然语言描述您的数据库查询需求"
                multiline
                rows={3}
                value={userPrompt}
                onChange={(e) => setUserPrompt(e.target.value)}
                placeholder="例如：查询最近10笔订单及其客户信息"
                variant="outlined"
                disabled={isGenerating || !isDatabaseConnected || isLoading}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                disabled={isGenerating || !isDatabaseConnected || !userPrompt.trim() || isLoading}
              >
                {isGenerating ? (
                  <>
                    <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                    生成中...
                  </>
                ) : (
                  '生成SQL查询'
                )}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
      
      {localError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {localError}
        </Alert>
      )}
      
      {aiResponse && (
        <Box mt={4}>
          <Typography variant="h5" gutterBottom>
            生成的SQL查询
          </Typography>
          
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                解释
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                {aiResponse.summary}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle1" gutterBottom>
                SQL查询
              </Typography>
              <SyntaxHighlighter language="sql" style={materialLight}>
                {aiResponse.query}
              </SyntaxHighlighter>
              
              <Button
                variant="outlined"
                color="primary"
                onClick={() => handleExecuteQuery(aiResponse.query)}
                disabled={isExecuting || isLoading}
                sx={{ mt: 2 }}
              >
                {isExecuting ? (
                  <>
                    <CircularProgress size={24} color="inherit" sx={{ mr: 1 }} />
                    执行中...
                  </>
                ) : (
                  '重新执行查询'
                )}
              </Button>
            </CardContent>
          </Card>
        </Box>
      )}
      
      {queryResults && queryResults.length > 0 && (
        <Box mt={4}>
          <Typography variant="h5" gutterBottom>
            查询结果
          </Typography>
          
          <TableContainer component={Paper}>
            <Table sx={{ minWidth: 650 }} aria-label="查询结果表">
              <TableHead>
                <TableRow>
                  {Object.keys(queryResults[0]).map((key) => (
                    <TableCell key={key}>{key}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {queryResults.map((row, index) => (
                  <TableRow key={index}>
                    {Object.values(row).map((value, i) => (
                      <TableCell key={i}>
                        {value === null ? 'NULL' : String(value)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
      
      {queryResults && queryResults.length === 0 && (
        <Box mt={4}>
          <Alert severity="info">查询执行成功，但没有返回任何结果</Alert>
        </Box>
      )}
    </div>
  );
};

export default Home;