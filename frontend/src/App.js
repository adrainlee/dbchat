import React, { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import Box from '@mui/material/Box';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Backdrop from '@mui/material/Backdrop';

import './App.css';
import { useAppContext } from './context/AppContext';

// 导入页面组件
import Home from './pages/Home';
import ConnectDb from './pages/ConnectDb';
import Settings from './pages/Settings';

function App() {
  // 从全局上下文获取状态
  const { 
    error, 
    successMessage, 
    isLoading,
    clearError, 
    clearSuccessMessage 
  } = useAppContext();

  // 主题模式状态（亮色/暗色）
  const [darkMode, setDarkMode] = useState(false);
  
  // 从localStorage加载主题设置
  useEffect(() => {
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode) {
      setDarkMode(savedMode === 'true');
    }
  }, []);

  // 创建主题
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
    },
  });

  // 切换主题模式
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', String(newMode));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, textAlign: 'left' }}>
              Python DB Chat Pro
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button color="inherit" component={Link} to="/">
                首页
              </Button>
              <Button color="inherit" component={Link} to="/connect">
                连接数据库
              </Button>
              <Button color="inherit" component={Link} to="/settings">
                设置
              </Button>
              <IconButton color="inherit" onClick={toggleDarkMode}>
                {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>
        <Container className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/connect" element={<ConnectDb />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Container>
        
        {/* 全局错误消息提示 */}
        <Snackbar
          open={Boolean(error)}
          autoHideDuration={6000}
          onClose={clearError}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        >
          <Alert
            onClose={clearError}
            severity="error"
            variant="filled"
            sx={{ width: '100%' }}
          >
            {error}
          </Alert>
        </Snackbar>
        
        {/* 全局成功消息提示 */}
        <Snackbar
          open={Boolean(successMessage)}
          autoHideDuration={3000}
          onClose={clearSuccessMessage}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        >
          <Alert
            onClose={clearSuccessMessage}
            severity="success"
            variant="filled"
            sx={{ width: '100%' }}
          >
            {successMessage}
          </Alert>
        </Snackbar>
        
        {/* 全局加载指示器 */}
        <Backdrop
          sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
          open={isLoading}
        >
          <CircularProgress color="inherit" />
        </Backdrop>
      </div>
    </ThemeProvider>
  );
}

export default App;