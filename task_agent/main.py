from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from pathlib import Path
from task_db import TaskDatabase

app = FastAPI(title="Task Agent", version="1.0.0")
db = TaskDatabase("tasks.db")

class TaskRequest(BaseModel):
    skill: str
    params: Dict[str, Any]

class TaskResponse(BaseModel):
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

@app.get("/.well-known/agent.json")
async def get_agent_card():
    """A2A検出用のエージェントカードを返す"""
    agent_card_path = Path(__file__).parent / "agent_card.json"
    with open(agent_card_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "agent": "task_agent"}

@app.post("/tasks", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """スキル名に基づいてタスクを実行"""
    try:
        skill = request.skill
        params = request.params
        
        if skill == "create_task":
            title = params.get("title")
            if not title:
                raise HTTPException(status_code=400, detail="title is required")
            
            description = params.get("description", "")
            priority = params.get("priority", "Medium")
            
            result = db.create_task(title, description, priority)
            return TaskResponse(
                status="ok",
                result=f"Task created successfully: '{title}' (ID: {result['id']}, Priority: {priority})"
            )
        
        elif skill == "list_tasks":
            status_filter = params.get("status")
            priority_filter = params.get("priority")
            
            tasks = db.list_tasks(status_filter, priority_filter)
            
            if not tasks:
                return TaskResponse(
                    status="ok",
                    result="No tasks found"
                )
            
            # 表示用にタスクをフォーマット
            task_list = []
            for task in tasks:
                status_icon = "✓" if task["status"] == "completed" else "○"
                priority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task["priority"], "")
                task_list.append(
                    f"{status_icon} [{task['id']}] {priority_icon} {task['title']}"
                    + (f" - {task['description']}" if task['description'] else "")
                )
            
            return TaskResponse(
                status="ok",
                result="\n".join(task_list)
            )
        
        elif skill == "get_task":
            task_id = params.get("task_id")
            if not task_id:
                raise HTTPException(status_code=400, detail="task_id is required")
            
            task = db.get_task(int(task_id))
            if not task:
                return TaskResponse(
                    status="error",
                    error=f"Task with ID {task_id} not found"
                )
            
            status_icon = "✓" if task["status"] == "completed" else "○"
            priority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task["priority"], "")
            
            result = (
                f"{status_icon} Task #{task['id']}\n"
                f"Title: {task['title']}\n"
                f"Priority: {priority_icon} {task['priority']}\n"
                f"Status: {task['status']}\n"
                f"Description: {task['description'] or 'N/A'}\n"
                f"Created: {task['created_at']}"
            )
            
            if task['completed_at']:
                result += f"\nCompleted: {task['completed_at']}"
            
            return TaskResponse(status="ok", result=result)
        
        elif skill == "complete_task":
            task_id = params.get("task_id")
            if not task_id:
                raise HTTPException(status_code=400, detail="task_id is required")
            
            success = db.complete_task(int(task_id))
            if not success:
                return TaskResponse(
                    status="error",
                    error=f"Task with ID {task_id} not found"
                )
            
            return TaskResponse(
                status="ok",
                result=f"Task #{task_id} marked as completed"
            )
        
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
    uvicorn.run(app, host="0.0.0.0", port=8003)

