import React, { useState } from 'react';
import {
  Typography,
  Box,
  Tab,
  Tabs,
  Paper,
} from '@mui/material';

// 导入全局状态
import { useAppContext } from '../context/AppContext';

// 导入拆分出的组件
import AIConnectionsTab from '../components/settings/AIConnectionsTab';
import HistoryTab from '../components/settings/HistoryTab';

// 选项卡面板组件
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Settings = () => {
  // 选项卡状态
  const [tabValue, setTabValue] = useState(0);
  
  // 使用全局状态
  const { setError, setSuccessMessage } = useAppContext();

  // 处理选项卡变更
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // 处理错误消息 - 转发到全局
  const handleError = (errorMessage) => {
    setError(errorMessage);
  };
  
  // 处理成功消息 - 转发到全局
  const handleSuccess = (message) => {
    setSuccessMessage(message);
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        设置
      </Typography>
      
      <Paper elevation={2}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="设置选项卡">
            <Tab label="AI连接" id="settings-tab-0" />
            <Tab label="历史记录" id="settings-tab-1" />
          </Tabs>
        </Box>
        
        {/* AI连接选项卡 */}
        <TabPanel value={tabValue} index={0}>
          <AIConnectionsTab 
            onError={handleError} 
            onSuccess={handleSuccess} 
          />
        </TabPanel>
        
        {/* 历史记录选项卡 */}
        <TabPanel value={tabValue} index={1}>
          <HistoryTab 
            onError={handleError} 
            onSuccess={handleSuccess}
          />
        </TabPanel>
      </Paper>
    </div>
  );
};

export default Settings;
