---
title: A2A Personal Assistant
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# A2A 个人助手

基于 A2A（Agent-to-Agent）协议的多智能体个人助手系统。五个独立服务通过 A2A 协议通信，处理邮件、日历和任务管理。

## 🎭 演示模式

本项目支持两种运行模式：

### 生产模式（main 分支）
- 需要 Google OAuth 凭证（`credentials.json`）
- 真实的 Gmail 和 Calendar API 调用
- 适合个人使用

### 演示模式（demo 分支）
- **无需 Google API 配置**
- 使用硬编码的模拟数据
- 适合快速体验和演示
- 🚀 **已部署到 HuggingFace Spaces**

## 系统架构

### 核心组件

1. **任务代理** (端口 8003)
   - 基于 SQLite 的本地任务管理
   - 技能：create_task, list_tasks, complete_task, get_task
   - 无外部依赖

2. **邮件代理** (端口 8001)
   - Gmail API 集成（OAuth2）
   - 技能：read_email, send_email, list_emails, search_emails
   - Token：`email_token.json`

3. **日历代理** (端口 8002)
   - Google Calendar API 集成（OAuth2）
   - 技能：list_events, create_event, today_schedule, get_event
   - Token：`calendar_token.json`

4. **协调器** (端口 8000)
   - Groq LLM 意图识别
   - 启动时自动发现代理
   - 路由查询到对应代理
   - 5层模型降级系统

5. **Streamlit UI** (端口 8501)
   - 聊天界面
   - 实时代理状态监控
   - 示例查询和聊天历史
   - 多语言支持（中文、日文、英文）

### 通信流程

```
用户 → UI (8501) → 协调器 (8000) → [任务/邮件/日历代理] → 响应
```

### Docker 部署架构（HuggingFace Spaces）

虽然运行在单个 Docker 容器中，但**所有 Agent 间的通信都是真实的 HTTP A2A 调用**：

```
Docker 容器 (HuggingFace Spaces)
├── Supervisor (进程管理)
│   ├── Orchestrator    (localhost:8000) ─┐
│   ├── Email Agent     (localhost:8001)  │
│   ├── Calendar Agent  (localhost:8002)  ├─ HTTP A2A 通信
│   ├── Task Agent      (localhost:8003)  │
│   └── Streamlit UI    (0.0.0.0:7860) ───┘
│
└── 对外暴露端口: 7860 (Streamlit UI)
```

**关键特性：**
- ✅ 真实的 Agent-to-Agent HTTP 调用（非函数调用）
- ✅ 每个 Agent 独立运行在自己的进程中
- ✅ 完整的 A2A 协议实现（Agent Card + /tasks 端点）
- ✅ Orchestrator 通过 HTTP 发现和调用其他 Agent
- ✅ 演示模式使用模拟数据，无需外部 API

## A2A 协议实现

每个代理实现以下端点：

1. **代理发现**：`GET /.well-known/agent.json`
   - 返回代理卡片（名称、描述、端点、技能）

2. **任务执行**：`POST /tasks`
   - 请求：`{"skill": "skill_name", "params": {...}}`
   - 响应：`{"status": "ok|error", "result": "...", "error": "..."}`

3. **健康检查**：`GET /health`
   - 返回代理状态和连接性

## 技术栈

- **后端**：FastAPI (Python)
- **前端**：Streamlit
- **LLM**：Groq API（5层降级）
- **数据库**：SQLite（任务代理）
- **API**：Gmail API, Google Calendar API
- **认证**：OAuth 2.0

## 核心特性

### 智能路由
- LLM 分析用户意图
- 自动选择正确的代理和技能
- 从自然语言提取参数

### 多代理协调
- 独立服务通过 HTTP 通信
- 启动时自动发现代理
- 优雅的错误处理

### OAuth 集成
- 安全的 Gmail 和 Calendar 访问
- Token 自动刷新
- 首次运行认证流程

### 多语言支持
- 完整的国际化（i18n）支持
- 支持语言：简体中文、日文、英文
- UI 所有元素实时响应语言切换：标题、标签、代理名称、示例查询
- 日文采用半角外来语格式
- 英文侧边栏标题特殊格式处理（换行显示）

### 模型降级系统
```python
TIER_TOP       = "openai/gpt-oss-120b"
TIER_UPPER_MID = "openai/gpt-oss-20b"
TIER_MID       = "qwen/qwen3-32b"
TIER_LOW       = "meta-llama/llama-4-scout-17b-16e-instruct"  # 默认
TIER_DEBUG     = "llama-3.1-8b-instant"  # 降级
```

遇到速率限制（429错误）时自动降级。

## 前置要求

- Python 3.8+
- Google Cloud 项目（已启用 Gmail 和 Calendar API）
- Groq API 密钥
- `credentials.json`（Google Cloud Console 的 OAuth 2.0 客户端 ID）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，添加 GROQ_API_KEY
```

### 3. Google OAuth 设置

- 确保 `credentials.json` 在项目根目录
- 首次运行时，每个代理会打开浏览器进行 OAuth 授权
- Token 会保存为 `email_token.json` 和 `calendar_token.json`

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

**手动启动（调试用）:**
```bash
# 终端 1 - 任务代理
cd task_agent && uvicorn main:app --port 8003

# 终端 2 - 日历代理
cd calendar_agent && uvicorn main:app --port 8002

# 终端 3 - 邮件代理
cd email_agent && uvicorn main:app --port 8001

# 终端 4 - 协调器
cd orchestrator && uvicorn main:app --port 8000

# 终端 5 - UI
cd ui && streamlit run app.py
```

### 5. 访问 UI

打开浏览器访问：http://localhost:8501

## 使用示例

### 语言切换
点击右侧边栏顶部的语言按钮（显示 `中/日/英`）选择不同语言：
- `中` - 简体中文
- `日` - 日本語
- `英` - English

所有 UI 元素会立即响应语言变化。

### 任务管理
- "创建一个高优先级任务来审查提案"
- "列出所有待办任务"
- "将任务1标记为完成"

### 邮件操作
- "显示最新的5封邮件"
- "搜索来自 john@example.com 的邮件"
- "给 jane@example.com 发送关于会议的邮件"

### 日历操作
- "今天的日程是什么？"
- "显示即将到来的活动"
- "明天下午2点创建一个会议"

## 项目结构

```
a2a-personal-assistant/
├── task_agent/
│   ├── main.py              # FastAPI 应用
│   ├── task_db.py           # SQLite 操作
│   ├── agent_card.json      # A2A 代理卡片
│   └── tasks.db             # 生成的数据库
├── email_agent/
│   ├── main.py              # FastAPI 应用
│   ├── gmail_client.py      # Gmail API 封装
│   ├── agent_card.json      # A2A 代理卡片
│   └── email_token.json     # OAuth token（生成）
├── calendar_agent/
│   ├── main.py              # FastAPI 应用
│   ├── calendar_client.py   # Calendar API 封装
│   ├── agent_card.json      # A2A 代理卡片
│   └── calendar_token.json  # OAuth token（生成）
├── orchestrator/
│   ├── main.py              # FastAPI 应用（含发现功能）
│   ├── llm_client.py        # Groq 客户端（含降级）
│   └── agent_card.json      # A2A 代理卡片
├── ui/
│   └── app.py               # Streamlit 界面
├── credentials.json         # Google OAuth 凭证
├── .env                     # 环境变量（需创建）
├── .env.example             # 环境变量模板
├── requirements.txt         # Python 依赖
├── start.bat                # Windows 启动脚本
├── start.sh                 # Linux/Mac 启动脚本
├── README.md                # 本文件
├── SETUP.md                 # 详细设置说明
└── TESTING.md               # 测试指南
```

## API 端点

### 任务代理 (8003)
- `GET /.well-known/agent.json` - 代理卡片
- `GET /health` - 健康检查
- `POST /tasks` - 执行任务

### 邮件代理 (8001)
- `GET /.well-known/agent.json` - 代理卡片
- `GET /health` - 健康检查
- `POST /tasks` - 执行任务

### 日历代理 (8002)
- `GET /.well-known/agent.json` - 代理卡片
- `GET /health` - 健康检查
- `POST /tasks` - 执行任务

### 协调器 (8000)
- `GET /.well-known/agent.json` - 代理卡片
- `GET /health` - 健康检查
- `GET /agents` - 列出已发现的代理
- `POST /query` - 处理用户查询
- `POST /rediscover` - 重新发现代理

### UI (8501)
- Web 界面：http://localhost:8501

## 性能指标

- **代理响应**：< 200ms（任务），1-3秒（邮件/日历）
- **LLM 路由**：2-5秒
- **端到端**：3-8秒
- **内存**：总计约 500MB
- **CPU**：空闲 < 5%，活动 < 30%

## 故障排除

### 常见问题

1. **端口冲突**：终止占用端口 8000-8003, 8501 的进程
2. **OAuth 错误**：删除 token 文件并重新认证
3. **代理未发现**：检查健康端点，触发重新发现
4. **速率限制**：系统自动降级到低层级模型

### 日志查看

检查各服务的终端窗口：
- 任务代理日志
- 邮件代理日志
- 日历代理日志
- 协调器日志
- Streamlit 日志

## 安全考虑

- OAuth token 本地存储（不在版本控制中）
- API 密钥在 `.env` 文件中（已 gitignore）
- 无硬编码凭证
- 生产环境建议使用 HTTPS

## 错误处理

- 代理不可用时优雅降级
- OAuth token 自动刷新
- 速率限制自动降级
- 无效技能/参数错误提示
- 网络超时处理

## 测试

详见 `TESTING.md`，包含：
- 单个代理测试
- A2A 协议测试
- 协调器路由测试
- UI 端到端测试
- 错误处理测试

## 依赖项

### 核心
- fastapi==0.115.0
- uvicorn[standard]==0.32.0
- streamlit==1.40.0
- groq==0.11.0

### Google APIs
- google-api-python-client==2.149.0
- google-auth-httplib2==0.2.0
- google-auth-oauthlib==1.2.1

### 工具
- python-dotenv==1.0.1
- requests==2.32.3
- pydantic==2.9.2

## 未来改进

- 添加更多代理（Slack、Notion 等）
- 实现代理间通信
- 添加对话记忆
- 支持多步骤工作流
- UI 添加认证
- 部署到云端
- 添加监控/指标
- 实现缓存
- 添加单元测试
- 支持多用户

## 项目状态

✅ 所有代理已实现  
✅ A2A 协议正常工作  
✅ 协调器 LLM 路由完成  
✅ Streamlit UI 功能正常  
✅ OAuth 集成完成  
✅ 启动脚本已创建  
✅ 文档完整  

**已就绪，可以开始测试和部署！**

## 支持

遇到问题时：
1. 查看 `SETUP.md` 了解设置说明
2. 查看 `TESTING.md` 了解测试步骤
3. 检查代理日志查找错误
4. 验证所有服务是否运行
5. 使用 curl 测试单个代理

## 许可证

MIT License