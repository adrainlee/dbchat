import React, { Component } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  Alert, 
  AlertTitle,
  Stack,
  Divider 
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import HomeIcon from '@mui/icons-material/Home';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  // 当子组件抛出错误时，这个生命周期方法会被调用
  static getDerivedStateFromError(error) {
    // 更新 state，下一次渲染将显示错误 UI
    return { hasError: true };
  }

  // 这个生命周期方法用于记录错误信息
  componentDidCatch(error, errorInfo) {
    // 可以在这里记录错误到错误报告服务
    console.error("错误边界捕获到错误:", error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  // 重置应用
  handleReset = () => {
    this.setState({ 
      hasError: false,
      error: null,
      errorInfo: null
    });
  }

  // 返回首页
  handleGoHome = () => {
    window.location.href = '/';
  }

  render() {
    if (this.state.hasError) {
      // 自定义错误显示
      return (
        <Box 
          display="flex" 
          justifyContent="center" 
          alignItems="center" 
          minHeight="100vh"
          bgcolor="#f5f5f5"
          p={3}
        >
          <Paper 
            elevation={3} 
            sx={{ 
              p: 4, 
              maxWidth: 600, 
              width: '100%',
              borderRadius: 2
            }}
          >
            <Alert severity="error" sx={{ mb: 3 }}>
              <AlertTitle>应用程序遇到问题</AlertTitle>
              我们的开发团队已收到此错误通知
            </Alert>
            
            <Typography variant="h5" gutterBottom color="error">
              发生了什么?
            </Typography>
            
            <Typography variant="body1" paragraph>
              应用程序在渲染过程中发生了错误。这可能是由于数据格式问题、网络错误或程序错误导致的。
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            {this.state.error && (
              <Box sx={{ mt: 2, mb: 3, p: 2, bgcolor: '#f8f8f8', borderRadius: 1, overflow: 'auto' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  错误详情:
                </Typography>
                <Typography variant="body2" component="pre" fontFamily="monospace" fontSize="0.8rem">
                  {this.state.error.toString()}
                </Typography>
              </Box>
            )}
            
            <Stack direction="row" spacing={2} justifyContent="center">
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<RefreshIcon />}
                onClick={this.handleReset}
              >
                尝试恢复
              </Button>
              <Button 
                variant="outlined"
                startIcon={<HomeIcon />}
                onClick={this.handleGoHome}
              >
                返回首页
              </Button>
            </Stack>
          </Paper>
        </Box>
      );
    }

    // 如果没有错误，正常渲染子组件
    return this.props.children;
  }
}

export default ErrorBoundary;