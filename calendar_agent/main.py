from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from calendar_client import CalendarClient

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(title="Calendar Agent", version="1.0.0")

# Check DEMO_MODE
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Initialize Calendar client (skip if in demo mode)
calendar = None
if not DEMO_MODE:
    try:
        calendar = CalendarClient()
    except Exception as e:
        print(f"Warning: Calendar client initialization failed: {e}")
else:
    print("📅 Calendar Agent running in DEMO MODE")

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
        "status": "healthy" if (calendar or DEMO_MODE) else "degraded",
        "agent": "calendar_agent",
        "calendar_connected": calendar is not None,
        "demo_mode": DEMO_MODE
    }

def format_datetime(dt_str: str) -> str:
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_str

def get_demo_events():
    """Return demo calendar events"""
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    return [
        {
            "id": "demo_event_001",
            "summary": "团队站会",
            "start": (today + timedelta(hours=9, minutes=30)).isoformat(),
            "end": (today + timedelta(hours=10)).isoformat(),
            "location": "会议室A",
            "description": "每日站会，同步项目进度和问题",
            "link": "https://meet.example.com/team-standup"
        },
        {
            "id": "demo_event_002",
            "summary": "产品需求评审",
            "start": (today + timedelta(hours=14)).isoformat(),
            "end": (today + timedelta(hours=16)).isoformat(),
            "location": "会议室B",
            "description": "评审下一版本的产品需求文档，讨论功能优先级",
            "link": "https://meet.example.com/product-review"
        },
        {
            "id": "demo_event_003",
            "summary": "技术分享会",
            "start": (today + timedelta(hours=16, minutes=30)).isoformat(),
            "end": (today + timedelta(hours=17, minutes=30)).isoformat(),
            "location": "线上会议",
            "description": "主题：微服务架构最佳实践",
            "link": "https://meet.example.com/tech-sharing"
        },
        {
            "id": "demo_event_004",
            "summary": "客户演示",
            "start": (tomorrow + timedelta(hours=10)).isoformat(),
            "end": (tomorrow + timedelta(hours=11, minutes=30)).isoformat(),
            "location": "会议室C",
            "description": "向客户演示新功能，准备demo环境",
            "link": "https://meet.example.com/client-demo"
        },
        {
            "id": "demo_event_005",
            "summary": "代码评审",
            "start": (tomorrow + timedelta(hours=15)).isoformat(),
            "end": (tomorrow + timedelta(hours=16)).isoformat(),
            "location": "线上会议",
            "description": "评审本周提交的代码，讨论改进建议",
            "link": "https://meet.example.com/code-review"
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
            
            if skill == "list_events":
                max_results = params.get("max_results", 10)
                demo_events = get_demo_events()[:max_results]
                
                if not demo_events:
                    return TaskResponse(status="ok", result="No upcoming events found (DEMO)")
                
                event_list = []
                for i, event in enumerate(demo_events, 1):
                    start = format_datetime(event['start'])
                    end = format_datetime(event['end'])
                    
                    event_str = f"{i}. 📅 {event['summary']}\n"
                    event_str += f"   ⏰ {start} - {end}"
                    
                    if event['location']:
                        event_str += f"\n   📍 {event['location']}"
                    
                    if event['description']:
                        desc = event['description'][:100]
                        event_str += f"\n   📝 {desc}..."
                    
                    event_list.append(event_str)
                
                result = "\n\n".join(event_list)
                return TaskResponse(status="ok", result=result)
            
            elif skill == "create_event":
                summary = params.get("summary", "")
                start_time = params.get("start_time", "")
                end_time = params.get("end_time", "")
                
                if not all([summary, start_time, end_time]):
                    raise HTTPException(
                        status_code=400,
                        detail="summary, start_time, and end_time are required"
                    )
                
                location = params.get("location", "")
                description = params.get("description", "")
                
                result = (
                    f"✅ Event created successfully! (DEMO)\n\n"
                    f"📅 {summary}\n"
                    f"⏰ {start_time} - {end_time}"
                )
                
                if location:
                    result += f"\n📍 {location}"
                
                result += "\n\n(This is a demo - no actual calendar event was created)"
                
                return TaskResponse(status="ok", result=result)
            
            elif skill == "today_schedule":
                demo_events = get_demo_events()
                today = datetime.now().date()
                
                # Filter events for today
                today_events = [
                    e for e in demo_events
                    if datetime.fromisoformat(e['start']).date() == today
                ]
                
                if not today_events:
                    return TaskResponse(
                        status="ok",
                        result="📅 No events scheduled for today (DEMO)"
                    )
                
                event_list = [f"📅 Today's Schedule ({len(today_events)} events) (DEMO):\n"]
                
                for i, event in enumerate(today_events, 1):
                    start = format_datetime(event['start'])
                    end = format_datetime(event['end'])
                    
                    event_str = f"{i}. {event['summary']}\n"
                    event_str += f"   ⏰ {start} - {end}"
                    
                    if event['location']:
                        event_str += f"\n   📍 {event['location']}"
                    
                    event_list.append(event_str)
                
                result = "\n\n".join(event_list)
                return TaskResponse(status="ok", result=result)
            
            elif skill == "get_event":
                event_id = params.get("event_id")
                if not event_id:
                    raise HTTPException(status_code=400, detail="event_id is required")
                
                demo_events = get_demo_events()
                event = next((e for e in demo_events if e["id"] == event_id), None)
                
                if not event:
                    return TaskResponse(
                        status="error",
                        error=f"Event with ID {event_id} not found (DEMO)"
                    )
                
                start = format_datetime(event['start'])
                end = format_datetime(event['end'])
                
                result = (
                    f"📅 Event Details (DEMO)\n\n"
                    f"Title: {event['summary']}\n"
                    f"⏰ {start} - {end}"
                )
                
                if event['location']:
                    result += f"\n📍 Location: {event['location']}"
                
                if event['description']:
                    result += f"\n📝 Description: {event['description']}"
                
                if event.get('link'):
                    result += f"\n🔗 Link: {event['link']}"
                
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
    
    # Real mode - use Calendar API
    if not calendar:
        return TaskResponse(
            status="error",
            error="Calendar client not initialized. Please check credentials and authentication."
        )
    
    try:
        skill = request.skill
        params = request.params
        
        if skill == "list_events":
            max_results = params.get("max_results", 10)
            time_min = params.get("time_min")
            
            events = calendar.list_events(max_results=max_results, time_min=time_min)
            
            if not events:
                return TaskResponse(status="ok", result="No upcoming events found")
            
            event_list = []
            for i, event in enumerate(events, 1):
                start = format_datetime(event['start'])
                end = format_datetime(event['end'])
                
                event_str = f"{i}. 📅 {event['summary']}\n"
                event_str += f"   ⏰ {start} - {end}"
                
                if event['location']:
                    event_str += f"\n   📍 {event['location']}"
                
                if event['description']:
                    desc = event['description'][:100]
                    event_str += f"\n   📝 {desc}..."
                
                event_list.append(event_str)
            
            result = "\n\n".join(event_list)
            return TaskResponse(status="ok", result=result)
        
        elif skill == "create_event":
            summary = params.get("summary")
            start_time = params.get("start_time")
            end_time = params.get("end_time")
            
            if not all([summary, start_time, end_time]):
                raise HTTPException(
                    status_code=400,
                    detail="summary, start_time, and end_time are required"
                )
            
            description = params.get("description", "")
            location = params.get("location", "")
            
            event = calendar.create_event(
                summary=summary,
                start_time=start_time,
                end_time=end_time,
                description=description,
                location=location
            )
            
            start = format_datetime(event['start'])
            end = format_datetime(event['end'])
            
            result = (
                f"✅ Event created successfully!\n\n"
                f"📅 {event['summary']}\n"
                f"⏰ {start} - {end}"
            )
            
            if location:
                result += f"\n📍 {location}"
            
            if event.get('link'):
                result += f"\n🔗 {event['link']}"
            
            return TaskResponse(status="ok", result=result)
        
        elif skill == "today_schedule":
            events = calendar.get_today_schedule()
            
            if not events:
                return TaskResponse(
                    status="ok",
                    result="📅 No events scheduled for today"
                )
            
            event_list = [f"📅 Today's Schedule ({len(events)} events):\n"]
            
            for i, event in enumerate(events, 1):
                start = format_datetime(event['start'])
                end = format_datetime(event['end'])
                
                event_str = f"{i}. {event['summary']}\n"
                event_str += f"   ⏰ {start} - {end}"
                
                if event['location']:
                    event_str += f"\n   📍 {event['location']}"
                
                event_list.append(event_str)
            
            result = "\n\n".join(event_list)
            return TaskResponse(status="ok", result=result)
        
        elif skill == "get_event":
            event_id = params.get("event_id")
            if not event_id:
                raise HTTPException(status_code=400, detail="event_id is required")
            
            event = calendar.get_event(event_id)
            if not event:
                return TaskResponse(
                    status="error",
                    error=f"Event with ID {event_id} not found"
                )
            
            start = format_datetime(event['start'])
            end = format_datetime(event['end'])
            
            result = (
                f"📅 Event Details\n\n"
                f"Title: {event['summary']}\n"
                f"⏰ {start} - {end}"
            )
            
            if event['location']:
                result += f"\n📍 Location: {event['location']}"
            
            if event['description']:
                result += f"\n📝 Description: {event['description']}"
            
            if event.get('link'):
                result += f"\n🔗 Link: {event['link']}"
            
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
    uvicorn.run(app, host="0.0.0.0", port=8002)

# Made with Bob
