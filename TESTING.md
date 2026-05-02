# A2A 个人助手 - 测试指南

## 测试前检查清单

- [ ] 已安装 Python 3.8+
- [ ] 已安装所有依赖（`pip install -r requirements.txt`）
- [ ] 已创建 `.env` 文件并配置有效的 `GROQ_API_KEY`
- [ ] 项目根目录存在 `credentials.json`
- [ ] 所有 5 个服务正在运行（使用 `start.bat` 或 `start.sh`）

## 测试 1：单个代理健康检查

### 任务代理（端口 8003）

```bash
# 健康检查
curl http://localhost:8003/health

# 预期响应：
# {"status":"healthy","agent":"task_agent"}

# 获取代理卡片
curl http://localhost:8003/.well-known/agent.json

# 预期：包含代理名称、描述、端点、技能的 JSON
```

### 邮件代理（端口 8001）

```bash
# 健康检查
curl http://localhost:8001/health

# 预期响应：
# {"status":"healthy","agent":"email_agent","gmail_connected":true}

# 获取代理卡片
curl http://localhost:8001/.well-known/agent.json
```

### 日历代理（端口 8002）

```bash
# 健康检查
curl http://localhost:8002/health

# 预期响应：
# {"status":"healthy","agent":"calendar_agent","calendar_connected":true}

# 获取代理卡片
curl http://localhost:8002/.well-known/agent.json
```

### 协调器（端口 8000）

```bash
# 健康检查
curl http://localhost:8000/health

# 预期响应：
# {"status":"healthy","agent":"orchestrator","discovered_agents":["task_agent","calendar_agent","email_agent"],"llm_available":true}

# 列出已发现的代理
curl http://localhost:8000/agents
```

## 测试 2：A2A 协议 - 直接调用代理

### 任务代理技能

**创建任务：**
```bash
curl -X POST http://localhost:8003/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "create_task",
    "params": {
      "title": "测试 A2A 协议",
      "description": "测试直接代理通信",
      "priority": "High"
    }
  }'

# 预期：{"status":"ok","result":"任务创建成功..."}
```

**列出任务：**
```bash
curl -X POST http://localhost:8003/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "list_tasks",
    "params": {}
  }'

# 预期：带图标和优先级的任务列表
```

**完成任务：**
```bash
curl -X POST http://localhost:8003/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "complete_task",
    "params": {
      "task_id": 1
    }
  }'

# 预期：{"status":"ok","result":"任务 #1 已标记为完成"}
```

### 邮件代理技能

**列出邮件：**
```bash
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "list_emails",
    "params": {
      "max_results": 5
    }
  }'

# 预期：最近邮件列表（包含主题和发件人）
```

**搜索邮件：**
```bash
curl -X POST http://localhost:8001/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "search_emails",
    "params": {
      "query": "subject:meeting",
      "max_results": 5
    }
  }'

# 预期：过滤后的邮件列表
```

### 日历代理技能

**今日日程：**
```bash
curl -X POST http://localhost:8002/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "today_schedule",
    "params": {}
  }'

# 预期：今日事件列表或"今天没有安排的事件"
```

**列出事件：**
```bash
curl -X POST http://localhost:8002/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "list_events",
    "params": {
      "max_results": 10
    }
  }'

# 预期：即将到来的日历事件列表
```

## 测试 3：协调器路由

### 测试意图识别

**任务创建：**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "创建一个高优先级任务来审查提案"
  }'

# 预期：
# - status: "ok"
# - agent_used: "task_agent"
# - skill_used: "create_task"
# - result: 任务创建确认
```

**邮件查询：**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "显示最新的 5 封邮件"
  }'

# 预期：
# - status: "ok"
# - agent_used: "email_agent"
# - skill_used: "list_emails"
# - result: 邮件列表
```

**日历查询：**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "今天的日程是什么？"
  }'

# 预期：
# - status: "ok"
# - agent_used: "calendar_agent"
# - skill_used: "today_schedule"
# - result: 今日日程
```

## 测试 4：UI 端到端测试

### 访问 UI
1. 在浏览器中打开 http://localhost:8501
2. 验证侧边栏中的"协调器在线"状态
3. 检查侧边栏中是否发现了所有 3 个代理

### 测试查询

**测试 1：任务管理**
```
查询："创建一个高优先级任务来准备演示文稿"
预期：成功消息（包含任务 ID）
```

**测试 2：邮件列表**
```
查询："显示我最新的邮件"
预期：最近邮件列表（包含主题和发件人）
```

**测试 3：日历检查**
```
查询："今天的日程是什么？"
预期：今日日程或"没有安排的事件"
```

**测试 4：复杂查询**
```
查询："列出所有待办任务"
预期：仅显示待办任务的过滤列表
```

**测试 5：邮件搜索**
```
查询："搜索关于会议的邮件"
预期：过滤后的邮件结果
```

### 验证 UI 功能

- [ ] 会话期间聊天历史保持
- [ ] 每个响应显示代理和技能名称
- [ ] 侧边栏中的示例查询点击后可用
- [ ] 清除聊天历史按钮有效
- [ ] 刷新状态按钮更新代理列表
- [ ] 错误消息清晰显示
- [ ] 处理期间显示加载动画
- [ ] 响应格式良好（邮件、事件、任务）

## 测试 5：错误处理

### 测试代理不可用

1. 停止一个代理（例如任务代理）
2. 尝试查询："创建一个任务来测试错误处理"
3. 预期：关于代理不可用的错误消息

### 测试无效技能

```bash
curl -X POST http://localhost:8003/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "invalid_skill",
    "params": {}
  }'

# 预期：{"status":"error","error":"未知技能: invalid_skill"}
```

### 测试缺少参数

```bash
curl -X POST http://localhost:8003/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "create_task",
    "params": {}
  }'

# 预期：关于缺少必需参数"title"的错误
```

## 测试 6：Groq 模型降级

### 模拟速率限制

如果遇到 Groq 速率限制，系统应自动在层级间降级：

1. `openai/gpt-oss-120b`（顶级）
2. `openai/gpt-oss-20b`
3. `qwen/qwen3-32b`
4. `meta-llama/llama-4-scout-17b-16e-instruct`
5. `llama-3.1-8b-instant`（降级）

监控协调器日志中的降级消息：
```
在 [model] 上遇到速率限制，降级到下一层...
```

## 测试 7：OAuth Token 刷新

### 测试 Token 过期

1. 删除 token 文件：
   ```bash
   rm email_agent/email_token.json
   rm calendar_agent/calendar_token.json
   ```

2. 重启邮件和日历代理
3. 在浏览器中完成 OAuth 流程
4. 验证重新认证后代理正常工作

## 测试结果检查清单

### 代理健康
- [ ] 任务代理响应健康检查
- [ ] 邮件代理响应健康检查
- [ ] 日历代理响应健康检查
- [ ] 协调器响应健康检查
- [ ] 所有代理返回有效的代理卡片

### A2A 协议
- [ ] 任务代理正确执行所有技能
- [ ] 邮件代理正确执行所有技能
- [ ] 日历代理正确执行所有技能
- [ ] 协调器在启动时发现所有代理
- [ ] 协调器将查询路由到正确的代理

### 意图识别
- [ ] 任务相关查询路由到任务代理
- [ ] 邮件相关查询路由到邮件代理
- [ ] 日历相关查询路由到日历代理
- [ ] 无效查询返回适当的错误

### UI 功能
- [ ] UI 正确加载和显示
- [ ] 聊天界面接受并显示消息
- [ ] 侧边栏显示代理状态
- [ ] 示例查询有效
- [ ] 错误消息正确显示
- [ ] 聊天历史保持

### 错误处理
- [ ] 缺少代理错误优雅处理
- [ ] 无效技能错误优雅处理
- [ ] 缺少参数错误优雅处理
- [ ] OAuth 错误优雅处理
- [ ] 速率限制降级有效

## 性能基准

### 预期响应时间

- **代理健康检查**：< 100ms
- **任务代理操作**：< 200ms
- **邮件代理操作**：1-3 秒（Gmail API）
- **日历代理操作**：1-3 秒（Calendar API）
- **协调器路由**：2-5 秒（包含 LLM）
- **端到端 UI 查询**：3-8 秒

### 资源使用

- **内存**：所有服务总计约 500MB
- **CPU**：空闲 < 5%，查询期间 < 30%
- **网络**：最小（仅 API 调用）

## 测试失败故障排除

### 代理无响应
1. 检查服务是否运行
2. 验证端口未被其他进程占用
3. 检查代理终端窗口中的日志

### OAuth 失败
1. 验证 `credentials.json` 有效
2. 删除 token 文件并重新认证
3. 检查 Google Cloud Console 中的 API 启用状态

### LLM 路由错误
1. 验证 `.env` 中的 `GROQ_API_KEY`
2. 检查 Groq API 配额/限制
3. 查看协调器日志中的错误

### UI 连接问题
1. 验证协调器在端口 8000 上运行
2. 检查浏览器控制台中的错误
3. 尝试刷新页面

## 成功标准

✅ 所有代理响应健康检查  
✅ 所有代理返回有效的代理卡片  
✅ 协调器发现所有 3 个代理  
✅ 所有技能的直接代理调用有效  
✅ 协调器正确路由查询  
✅ UI 正确显示和运行  
✅ 错误处理按预期工作  
✅ OAuth 认证成功  
✅ 端到端工作流成功完成  

## 测试后的下一步

1. 监控日志中的任何警告或错误
2. 使用真实世界的查询进行测试
3. 验证 Gmail 和 Calendar 操作与实际数据
4. 测试并发请求
5. 如需要，测量和优化性能