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
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { historyApi } from '../../services/api';

const HistoryTab = ({ onError, onSuccess }) => {
  // 历史记录状态
  const [historyItems, setHistoryItems] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isClearingHistory, setIsClearingHistory] = useState(false);
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

  // 获取历史记录
  useEffect(() => {
    loadHistoryItems();
  }, []);
  
  // 加载历史记录
  const loadHistoryItems = async () => {
    setIsLoadingHistory(true);
    
    try {
      const items = await historyApi.getHistoryItems();
      setHistoryItems(items);
    } catch (error) {
      console.error('获取历史记录错误:', error);
      onError && onError('获取历史记录失败');
    } finally {
      setIsLoadingHistory(false);
    }
  };
  
  // 删除历史记录项
  const handleDeleteHistoryItem = async (itemId) => {
    try {
      await historyApi.deleteHistoryItem(itemId);
      setHistoryItems(historyItems.filter(item => item.id !== itemId));
      onSuccess && onSuccess('成功删除历史记录项');
      
      if (selectedHistoryItem && selectedHistoryItem.id === itemId) {
        setSelectedHistoryItem(null);
      }
    } catch (error) {
      onError && onError(`删除历史记录错误: ${error.message}`);
    }
  };
  
  // 清空所有历史
  const handleClearHistory = async () => {
    setIsClearingHistory(true);
    
    try {
      await historyApi.clearHistory();
      setHistoryItems([]);
      setSelectedHistoryItem(null);
      onSuccess && onSuccess('成功清空所有历史记录');
    } catch (error) {
      onError && onError(`清空历史记录错误: ${error.message}`);
    } finally {
      setIsClearingHistory(false);
    }
  };
  
  // 查看历史记录详情
  const handleViewHistoryItem = (item) => {
    setSelectedHistoryItem(item);
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={5}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">查询历史</Typography>
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<DeleteIcon />}
            onClick={handleClearHistory}
            disabled={isClearingHistory || historyItems.length === 0}
          >
            {isClearingHistory ? '清空中...' : '清空历史'}
          </Button>
        </Box>
        
        {isLoadingHistory ? (
          <Box display="flex" justifyContent="center" my={3}>
            <CircularProgress />
          </Box>
        ) : historyItems.length === 0 ? (
          <Alert severity="info">
            没有查询历史记录。
          </Alert>
        ) : (
          <Paper elevation={2} sx={{ maxHeight: '70vh', overflow: 'auto' }}>
            <List>
              {historyItems.map((item, index) => (
                <React.Fragment key={item.id}>
                  {index > 0 && <Divider />}
                  <ListItem
                    button
                    selected={selectedHistoryItem && selectedHistoryItem.id === item.id}
                    onClick={() => handleViewHistoryItem(item)}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        aria-label="删除"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteHistoryItem(item.id);
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    }
                  >
                    <ListItemText
                      primary={item.prompt.length > 50 ? item.prompt.substring(0, 50) + '...' : item.prompt}
                      secondary={new Date(item.timestamp).toLocaleString()}
                    />
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </Paper>
        )}
      </Grid>
      
      <Grid item xs={12} md={7}>
        {selectedHistoryItem ? (
          <Paper elevation={3} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              查询详情
            </Typography>
            
            <Typography variant="subtitle2">提示:</Typography>
            <Typography variant="body2" paragraph>
              {selectedHistoryItem.prompt}
            </Typography>
            
            <Typography variant="subtitle2">解释:</Typography>
            <Typography variant="body2" paragraph>
              {selectedHistoryItem.summary}
            </Typography>
            
            <Typography variant="subtitle2">SQL查询:</Typography>
            <SyntaxHighlighter language="sql" style={materialLight}>
              {selectedHistoryItem.query}
            </SyntaxHighlighter>
          </Paper>
        ) : (
          <Paper elevation={3} sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
            <Typography variant="body1" color="textSecondary">
              从左侧选择一个历史记录项查看详情
            </Typography>
          </Paper>
        )}
      </Grid>
    </Grid>
  );
};

export default HistoryTab;