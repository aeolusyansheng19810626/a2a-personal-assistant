# A2A 个人助手 - 安装指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

在项目根目录创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 Groq API 密钥：

```
GROQ_API_KEY=你的实际groq_api密钥
```

**获取 Groq API 密钥：** https://console.groq.com/keys

### 3. Google OAuth 设置

你的 `credentials.json` 已经就位。首次运行时：

1. **邮件代理** 会打开浏览器进行 Gmail OAuth 授权
   - 授予 Gmail 访问权限（读取、发送、修改）
   - Token 保存为 `email_token.json`

2. **日历代理** 会打开浏览器进行 Calendar OAuth 授权
   - 授予 Google Calendar 访问权限（读取、写入事件）
   - Token 保存为 `calendar_token.json`

### 4. 启动系统

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

这将在独立的终端窗口中启动所有 5 个服务：
- 任务代理（端口 8003）
- 日历代理（端口 8002）
- 邮件代理（端口 8001）
- 协调器（端口 8000）
- Streamlit UI（端口 8501）

### 5. 访问 UI

在浏览器中打开：**http://localhost:8501**

## 手动启动（用于调试）

在独立的终端中启动每个服务：

```bash
# 终端 1 - 任务代理
cd task_agent
uvicorn main:app --port 8003

# 终端 2 - 日历代理
cd calendar_agent
uvicorn main:app --port 8002

# 终端 3 - 邮件代理
cd email_agent
uvicorn main:app --port 8001

# 终端 4 - 协调器
cd orchestrator
uvicorn main:app --port 8000

# 终端 5 - UI
cd ui
streamlit run app.py
```

## 测试单个代理

### 任务代理 (http://localhost:8003)

```bash
# 获取代理卡片
curl http://localhost:8003/.well-known/agent.json

# 创建任务
curl -X POST http://localhost:8003/tasks \
  -H "Content-Type: application/json" \
  -d '{"skill": "create_task", "params": {"title": "测试任务", "priority": "High"}}'

# 列出任务
curl -X POST http://localhost:8003/tasks \
  -H "Content-Type: application/json" \
  -d '{"skill": "list_tasks", "params": {}}'
```

### 邮件代理 (http://localhost:8001)

```bash
# 获取代理卡片
curl http://localhost:8001/.well-known/agent.json

# 列出邮件
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{"skill": "list_emails", "params": {"max_results": 5}}'
```

### 日历代理 (http://localhost:8002)

```bash
# 获取代理卡片
curl http://localhost:8002/.well-known/agent.json

# 获取今日日程
curl -X POST http://localhost:8002/tasks \
  -H "Content-Type: application/json" \
  -d '{"skill": "today_schedule", "params": {}}'
```

### 协调器 (http://localhost:8000)

```bash
# 检查健康状态和已发现的代理
curl http://localhost:8000/health

# 列出所有代理
curl http://localhost:8000/agents

# 发送查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "创建一个高优先级任务来审查提案"}'
```

## 故障排除

### 端口已被占用

如果遇到"端口已被占用"错误：

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:8000 | xargs kill -9
```

### OAuth Token 问题

如果遇到认证错误：

1. 删除 token 文件：
   ```bash
   rm email_token.json calendar_token.json
   ```

2. 重启代理 - 它们会重新认证

### Groq API 速率限制

系统会自动在 5 个模型层级间降级：
1. `openai/gpt-oss-120b`（顶级）
2. `openai/gpt-oss-20b`
3. `qwen/qwen3-32b`
4. `meta-llama/llama-4-scout-17b-16e-instruct`（默认用于意图识别）
5. `llama-3.1-8b-instant`（降级）

如果遇到速率限制，系统会自动使用较低层级。

### 代理未被发现

如果协调器找不到代理：

1. 确保所有代理都在运行
2. 检查代理健康端点：
   - http://localhost:8003/health
   - http://localhost:8002/health
   - http://localhost:8001/health

3. 手动触发重新发现：
   ```bash
   curl -X POST http://localhost:8000/rediscover
   ```

### Gmail/Calendar API 错误

常见问题：

1. **找不到凭证**：确保 `credentials.json` 在项目根目录
2. **作用域不匹配**：删除 token 文件并重新认证
3. **API 未启用**：在 Google Cloud Console 中启用 Gmail 和 Calendar API

## 示例查询

在 UI 中尝试这些查询：

**任务：**
- "创建一个高优先级任务来审查提案"
- "列出所有待办任务"
- "显示我的任务"
- "将任务 1 标记为完成"

**邮件：**
- "显示最新的 5 封邮件"
- "搜索来自 john@example.com 的邮件"
- "给 jane@example.com 发送关于明天会议的邮件"

**日历：**
- "今天的日程是什么？"
- "显示即将到来的活动"
- "明天下午 2 点创建一个会议"

**复杂查询：**
- "检查我的邮件并为任何行动项创建任务"
- "本周我有什么安排？"

## 架构

```
用户查询 → Streamlit UI (8501)
    ↓
协调器 (8000) [Groq LLM 意图识别]
    ↓
A2A 协议 (HTTP POST /tasks)
    ↓
┌─────────────┬──────────────┬─────────────┐
│ 任务代理    │ 邮件代理     │ 日历代理    │
│ (8003)      │ (8001)       │ (8002)      │
│ SQLite      │ Gmail API    │ Calendar API│
└─────────────┴──────────────┴─────────────┘
```

## 文件结构

```
a2a-personal-assistant/
├── task_agent/
│   ├── main.py              # FastAPI 应用
│   ├── task_db.py           # SQLite 操作
│   ├── agent_card.json      # A2A 代理卡片
│   └── tasks.db             # 首次运行时生成
├── email_agent/
│   ├── main.py              # FastAPI 应用
│   ├── gmail_client.py      # Gmail API 封装
│   ├── agent_card.json      # A2A 代理卡片
│   └── email_token.json     # OAuth 时生成
├── calendar_agent/
│   ├── main.py              # FastAPI 应用
│   ├── calendar_client.py   # Calendar API 封装
│   ├── agent_card.json      # A2A 代理卡片
│   └── calendar_token.json  # OAuth 时生成
├── orchestrator/
│   ├── main.py              # FastAPI 应用（含 A2A 发现）
│   ├── llm_client.py        # Groq 客户端（含层级降级）
│   └── agent_card.json      # A2A 代理卡片
├── ui/
│   └── app.py               # Streamlit 聊天界面
├── credentials.json         # Google OAuth 凭证
├── .env                     # 环境变量（需创建）
├── requirements.txt         # Python 依赖
├── start.bat                # Windows 启动脚本
└── start.sh                 # Linux/Mac 启动脚本
```

## 下一步

1. ✅ 安装依赖
2. ✅ 配置 `.env` 文件（添加 Groq API 密钥）
3. ✅ 运行 `start.bat` 或 `start.sh`
4. ✅ 完成 Gmail 和 Calendar 的 OAuth 授权
5. ✅ 打开 http://localhost:8501
6. ✅ 开始与你的助手聊天！

## 支持

遇到问题或疑问时：
- 查看上面的故障排除部分
- 在代理的终端窗口中查看日志
- 使用 curl 命令测试单个代理
- 通过健康检查验证所有服务是否运行