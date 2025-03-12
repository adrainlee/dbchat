# DBChat - AI数据库助手

一个使用Python和React构建的AI驱动的数据库查询助手，允许用户使用自然语言生成和执行SQL查询。

## 功能

- 使用自然语言生成SQL查询
- 支持多种数据库（MySQL, PostgreSQL, SQL Server）
- 多种AI模型集成（OpenAI, Azure OpenAI, Ollama）
- 查询历史记录管理
- 可自定义AI连接配置
- 响应式Web界面

## 技术栈

### 后端
- FastAPI - 高性能异步API框架
- SQLAlchemy - ORM和数据库抽象
- Pydantic - 数据验证
- 异步数据库驱动 (aiomysql, asyncpg, aioodbc)

### 前端
- React - UI组件库
- Material-UI - 组件库和设计系统
- React Router - 导航
- React Context API - 状态管理

## 快速开始

### 后端设置

1. 设置Python环境：

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows中使用: venv\Scripts\activate
pip install -r requirements.txt
```

2. 配置环境变量：

```bash
cp .env.example .env
# 编辑.env文件，添加您的数据库和AI服务凭据
```

3. 启动后端服务器：

```bash
uvicorn app.main:app --reload
```

### 前端设置

1. 安装依赖：

```bash
cd frontend
npm install
```

2. 启动开发服务器：

```bash
npm start
```

## 使用方法

1. 打开应用程序并导航到"连接数据库"页面
2. 输入您的数据库连接字符串
3. 切换到主页，使用自然语言描述您的查询需求
4. 生成的SQL查询将显示并自动执行
5. 可以在设置页面查看历史记录和管理AI连接

## 许可证

MIT