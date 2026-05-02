from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import requests
from pathlib import Path
from llm_client import GroqClient

app = FastAPI(title="Orchestrator", version="1.0.0")

# Agent registry
agent_registry: Dict[str, Dict[str, Any]] = {}

# Initialize Groq client
try:
    llm_client = GroqClient()
except Exception as e:
    print(f"Warning: Groq client initialization failed: {e}")
    llm_client = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    agent_used: Optional[str] = None
    skill_used: Optional[str] = None

def discover_agents():
    """Discover all agents by calling their agent card endpoints"""
    agent_ports = {
        "task_agent": 8003,
        "calendar_agent": 8002,
        "email_agent": 8001
    }
    
    discovered = {}
    
    for agent_name, port in agent_ports.items():
        try:
            response = requests.get(
                f"http://localhost:{port}/.well-known/agent.json",
                timeout=2
            )
            
            if response.status_code == 200:
                agent_card = response.json()
                discovered[agent_name] = agent_card
                print(f"✓ Discovered {agent_name} at port {port}")
            else:
                print(f"✗ Failed to discover {agent_name}: HTTP {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to discover {agent_name}: {e}")
    
    return discovered

@app.on_event("startup")
async def startup_event():
    """Discover agents on startup"""
    global agent_registry
    print("Starting agent discovery...")
    agent_registry = discover_agents()
    print(f"Discovery complete. Found {len(agent_registry)} agents.")

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
        "status": "healthy",
        "agent": "orchestrator",
        "discovered_agents": list(agent_registry.keys()),
        "llm_available": llm_client is not None
    }

@app.get("/agents")
async def list_agents():
    """List all discovered agents"""
    return {
        "agents": agent_registry,
        "count": len(agent_registry)
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query and route to appropriate agent"""
    if not llm_client:
        return QueryResponse(
            status="error",
            error="LLM client not initialized. Please check GROQ_API_KEY."
        )
    
    if not agent_registry:
        return QueryResponse(
            status="error",
            error="No agents discovered. Please ensure agents are running."
        )
    
    try:
        # Parse intent using LLM
        intent = llm_client.parse_intent(request.query, agent_registry)
        
        agent_name = intent.get("agent")
        skill_name = intent.get("skill")
        params = intent.get("params", {})
        reasoning = intent.get("reasoning", "")
        
        # Check if agent was identified
        if agent_name == "none" or agent_name not in agent_registry:
            return QueryResponse(
                status="error",
                error=f"Could not route query to any agent. {reasoning}",
                agent_used=None,
                skill_used=None
            )
        
        # Get agent endpoint
        agent_card = agent_registry[agent_name]
        agent_endpoint = agent_card.get("endpoint")
        
        if not agent_endpoint:
            return QueryResponse(
                status="error",
                error=f"Agent {agent_name} has no endpoint configured"
            )
        
        # Call agent's /tasks endpoint
        task_request = {
            "skill": skill_name,
            "params": params
        }
        
        response = requests.post(
            f"{agent_endpoint}/tasks",
            json=task_request,
            timeout=30
        )
        
        if response.status_code != 200:
            return QueryResponse(
                status="error",
                error=f"Agent returned HTTP {response.status_code}",
                agent_used=agent_name,
                skill_used=skill_name
            )
        
        agent_response = response.json()
        
        if agent_response.get("status") == "error":
            return QueryResponse(
                status="error",
                error=agent_response.get("error", "Unknown error from agent"),
                agent_used=agent_name,
                skill_used=skill_name
            )
        
        return QueryResponse(
            status="ok",
            result=agent_response.get("result"),
            agent_used=agent_name,
            skill_used=skill_name
        )
    
    except requests.exceptions.RequestException as e:
        return QueryResponse(
            status="error",
            error=f"Failed to communicate with agent: {str(e)}",
            agent_used=agent_name if 'agent_name' in locals() else None,
            skill_used=skill_name if 'skill_name' in locals() else None
        )
    
    except Exception as e:
        return QueryResponse(
            status="error",
            error=f"Orchestrator error: {str(e)}"
        )

@app.post("/rediscover")
async def rediscover_agents():
    """Manually trigger agent rediscovery"""
    global agent_registry
    agent_registry = discover_agents()
    return {
        "status": "ok",
        "discovered_agents": list(agent_registry.keys()),
        "count": len(agent_registry)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
