from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from gmail_client import GmailClient

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(title="Email Agent", version="1.0.0")

# Check DEMO_MODE
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Initialize Gmail client (skip if in demo mode)
gmail = None
if not DEMO_MODE:
    try:
        gmail = GmailClient()
    except Exception as e:
        print(f"Warning: Gmail client initialization failed: {e}")
else:
    print("📧 Email Agent running in DEMO MODE")

class TaskRequest(BaseModel):
    skill: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Return agent card for A2A discovery"""
    agent_card_path = Path(__file__).parent / "agent_card.json"
    with open(agent_card_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if (gmail or DEMO_MODE) else "degraded",
        "agent": "email_agent",
        "gmail_connected": gmail is not None,
        "demo_mode": DEMO_MODE
    }

def get_demo_emails():
    """Return demo email data"""
    return [
        {
            "id": "demo_001",
            "from": "张三 <zhangsan@example.com>",
            "subject": "项目进度更新",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "snippet": "本周项目进展顺利，已完成核心功能开发，预计下周可以进入测试阶段...",
            "body": "你好，\n\n本周项目进展顺利，已完成核心功能开发，预计下周可以进入测试阶段。\n\n主要完成内容：\n1. 用户认证模块\n2. 数据库设计\n3. API接口开发\n\n下周计划：\n- 单元测试\n- 集成测试\n- 性能优化\n\n如有问题请随时联系。\n\n张三"
        },
        {
            "id": "demo_002",
            "from": "李四 <lisi@company.com>",
            "subject": "会议邀请：技术评审",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "snippet": "邀请您参加明天下午2点的技术评审会议，讨论新功能的技术方案...",
            "body": "你好，\n\n邀请您参加明天下午2点的技术评审会议。\n\n会议主题：新功能技术方案评审\n时间：明天 14:00-16:00\n地点：会议室A\n\n议程：\n1. 技术方案介绍\n2. 架构设计讨论\n3. 风险评估\n\n请提前准备相关材料。\n\n李四"
        },
        {
            "id": "demo_003",
            "from": "王五 <wangwu@partner.com>",
            "subject": "合作提案",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "snippet": "我们对贵公司的产品很感兴趣，希望能探讨合作机会...",
            "body": "您好，\n\n我是XX公司的王五，我们对贵公司的产品很感兴趣。\n\n我们希望能够：\n1. 了解产品的详细功能\n2. 讨论合作模式\n3. 商谈价格方案\n\n方便的话，我们可以安排一次线上会议详细沟通。\n\n期待您的回复。\n\n王五\nXX公司"
        },
        {
            "id": "demo_004",
            "from": "系统通知 <noreply@system.com>",
            "subject": "账户安全提醒",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "snippet": "检测到您的账户在新设备上登录，如非本人操作请立即修改密码...",
            "body": "尊敬的用户，\n\n我们检测到您的账户在新设备上登录：\n\n登录时间：今天 10:30\n登录地点：北京\n设备类型：Windows PC\n\n如果这是您本人的操作，请忽略此邮件。\n如果不是，请立即：\n1. 修改密码\n2. 启用两步验证\n3. 检查账户活动记录\n\n系统安全团队"
        },
        {
            "id": "demo_005",
            "from": "赵六 <zhaoliu@team.com>",
            "subject": "周报提交提醒",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "snippet": "请记得在本周五下班前提交本周工作周报...",
            "body": "各位同事，\n\n请记得在本周五（5月3日）下班前提交本周工作周报。\n\n周报内容应包括：\n1. 本周完成的工作\n2. 遇到的问题和解决方案\n3. 下周工作计划\n\n提交方式：发送至 report@team.com\n\n谢谢配合！\n\n赵六\n项目经理"
        }
    ]

@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """Execute a task based on skill name"""
    # In demo mode, use mock data
    if DEMO_MODE:
        try:
            skill = request.skill
            params = request.params
            
            if skill == "read_email":
                demo_emails = get_demo_emails()
                message_id = params.get("message_id")
                count = params.get("count", 5)
                
                if message_id:
                    # Find specific email
                    email = next((e for e in demo_emails if e["id"] == message_id), None)
                    if not email:
                        return TaskResponse(
                            status="error",
                            error=f"Email with ID {message_id} not found"
                        )
                    
                    result = (
                        f"📧 Email Details (DEMO)\n"
                        f"From: {email['from']}\n"
                        f"Subject: {email['subject']}\n"
                        f"Date: {email['date']}\n"
                        f"\n{email['body']}"
                    )
                else:
                    # Get latest emails
                    emails = demo_emails[:count]
                    email_list = []
                    for email in emails:
                        email_list.append(
                            f"📧 {email['subject']}\n"
                            f"   From: {email['from']}\n"
                            f"   {email['snippet'][:100]}..."
                        )
                    result = "\n\n".join(email_list)
                
                return TaskResponse(status="ok", result=result)
            
            elif skill == "send_email":
                to = params.get("to", "")
                subject = params.get("subject", "")
                body = params.get("body", "")
                
                if not all([to, subject, body]):
                    raise HTTPException(
                        status_code=400,
                        detail="to, subject, and body are required"
                    )
                
                return TaskResponse(
                    status="ok",
                    result=f"✅ Email sent successfully (DEMO)\nTo: {to}\nSubject: {subject}\n\n(This is a demo - no actual email was sent)"
                )
            
            elif skill == "list_emails":
                max_results = params.get("max_results", 10)
                demo_emails = get_demo_emails()[:max_results]
                
                email_list = []
                for i, email in enumerate(demo_emails, 1):
                    email_list.append(
                        f"{i}. 📧 {email['subject']}\n"
                        f"   From: {email['from']}\n"
                        f"   Date: {email['date']}\n"
                        f"   {email['snippet'][:100]}..."
                    )
                
                result = "\n\n".join(email_list)
                return TaskResponse(status="ok", result=result)
            
            elif skill == "search_emails":
                query = params.get("query", "")
                if not query:
                    raise HTTPException(status_code=400, detail="query is required")
                
                # Simple demo search - filter by subject or body
                demo_emails = get_demo_emails()
                filtered = [e for e in demo_emails if query.lower() in e['subject'].lower() or query.lower() in e['body'].lower()]
                
                if not filtered:
                    return TaskResponse(
                        status="ok",
                        result=f"No emails found matching query: {query} (DEMO)"
                    )
                
                email_list = []
                for i, email in enumerate(filtered, 1):
                    email_list.append(
                        f"{i}. 📧 {email['subject']}\n"
                        f"   From: {email['from']}\n"
                        f"   Date: {email['date']}\n"
                        f"   {email['snippet'][:100]}..."
                    )
                
                result = f"Search results for '{query}' (DEMO):\n\n" + "\n\n".join(email_list)
                return TaskResponse(status="ok", result=result)
            
            else:
                return TaskResponse(
                    status="error",
                    error=f"Unknown skill: {skill}"
                )
        
        except Exception as e:
            return TaskResponse(
                status="error",
                error=str(e)
            )
    
    # Real mode - use Gmail API
    if not gmail:
        return TaskResponse(
            status="error",
            error="Gmail client not initialized. Please check credentials and authentication."
        )
    
    try:
        skill = request.skill
        params = request.params
        
        if skill == "read_email":
            message_id = params.get("message_id")
            count = params.get("count", 5)
            
            if message_id:
                # Read specific email
                email = gmail.get_email(message_id)
                if not email:
                    return TaskResponse(
                        status="error",
                        error=f"Email with ID {message_id} not found"
                    )
                
                result = (
                    f"📧 Email Details\n"
                    f"From: {email['from']}\n"
                    f"Subject: {email['subject']}\n"
                    f"Date: {email['date']}\n"
                    f"\n{email['body']}"
                )
            else:
                # Get latest emails
                emails = gmail.list_emails(max_results=count)
                if not emails:
                    return TaskResponse(status="ok", result="No emails found")
                
                email_list = []
                for email in emails:
                    email_list.append(
                        f"📧 {email['subject']}\n"
                        f"   From: {email['from']}\n"
                        f"   {email['snippet'][:100]}..."
                    )
                
                result = "\n\n".join(email_list)
            
            return TaskResponse(status="ok", result=result)
        
        elif skill == "send_email":
            to = params.get("to")
            subject = params.get("subject")
            body = params.get("body")
            
            if not all([to, subject, body]):
                raise HTTPException(
                    status_code=400,
                    detail="to, subject, and body are required"
                )
            
            result = gmail.send_email(to, subject, body)
            return TaskResponse(
                status="ok",
                result=f"✅ Email sent successfully to {to}\nSubject: {subject}"
            )
        
        elif skill == "list_emails":
            max_results = params.get("max_results", 10)
            query = params.get("query", "")
            
            emails = gmail.list_emails(max_results=max_results, query=query)
            
            if not emails:
                return TaskResponse(status="ok", result="No emails found")
            
            email_list = []
            for i, email in enumerate(emails, 1):
                email_list.append(
                    f"{i}. 📧 {email['subject']}\n"
                    f"   From: {email['from']}\n"
                    f"   Date: {email['date']}\n"
                    f"   {email['snippet'][:100]}..."
                )
            
            result = "\n\n".join(email_list)
            return TaskResponse(status="ok", result=result)
        
        elif skill == "search_emails":
            query = params.get("query")
            if not query:
                raise HTTPException(status_code=400, detail="query is required")
            
            max_results = params.get("max_results", 10)
            emails = gmail.search_emails(query, max_results=max_results)
            
            if not emails:
                return TaskResponse(
                    status="ok",
                    result=f"No emails found matching query: {query}"
                )
            
            email_list = []
            for i, email in enumerate(emails, 1):
                email_list.append(
                    f"{i}. 📧 {email['subject']}\n"
                    f"   From: {email['from']}\n"
                    f"   Date: {email['date']}\n"
                    f"   {email['snippet'][:100]}..."
                )
            
            result = f"Search results for '{query}':\n\n" + "\n\n".join(email_list)
            return TaskResponse(status="ok", result=result)
        
        else:
            return TaskResponse(
                status="error",
                error=f"Unknown skill: {skill}"
            )
    
    except Exception as e:
        return TaskResponse(
            status="error",
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

# Made with Bob
