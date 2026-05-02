import os
from typing import Optional, Dict, Any
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# Load .env from parent directory (project root)
load_dotenv(Path(__file__).parent.parent / ".env")

# Groq model tiers with fallback
TIER_TOP = "openai/gpt-oss-120b"
TIER_UPPER_MID = "openai/gpt-oss-20b"
TIER_MID = "qwen/qwen3-32b"
TIER_LOW = "meta-llama/llama-4-scout-17b-16e-instruct"
TIER_DEBUG = "llama-3.1-8b-instant"

MODEL_TIERS = [TIER_TOP, TIER_UPPER_MID, TIER_MID, TIER_LOW, TIER_DEBUG]

class GroqClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Remove proxies parameter - not supported in current Groq version
        self.client = Groq(api_key=api_key)
        self.current_tier_index = 3  # Start with TIER_LOW for intent recognition
    
    def chat_completion(self, messages: list, model: Optional[str] = None, 
                       temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send chat completion request with automatic tier fallback on 429 errors
        """
        if model:
            # Use specified model
            return self._make_request(messages, model, temperature, max_tokens)
        
        # Use tier system with fallback
        tier_index = self.current_tier_index
        
        while tier_index < len(MODEL_TIERS):
            try:
                model = MODEL_TIERS[tier_index]
                response = self._make_request(messages, model, temperature, max_tokens)
                return response
            
            except Exception as e:
                error_str = str(e)
                
                # Check for rate limit (429) error
                if "429" in error_str or "rate_limit" in error_str.lower():
                    print(f"Rate limit hit on {model}, falling back to next tier...")
                    tier_index += 1
                    
                    if tier_index >= len(MODEL_TIERS):
                        raise Exception("All model tiers exhausted due to rate limits")
                else:
                    # Other errors, re-raise
                    raise
        
        raise Exception("Failed to get response from any model tier")
    
    def _make_request(self, messages: list, model: str, 
                     temperature: float, max_tokens: int) -> str:
        """Make actual API request"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return chat_completion.choices[0].message.content or ""
        
        except Exception as e:
            raise Exception(f"Groq API error with model {model}: {str(e)}")
    
    def parse_intent(self, user_query: str, agent_cards: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse user intent and determine which agent and skill to use
        """
        from datetime import datetime, timedelta
        
        # Get current date/time for context
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        
        # Format agent cards for prompt with detailed skill parameters
        agents_info = []
        for agent_name, card in agent_cards.items():
            agent_desc = f"- {agent_name}: {card.get('description', '')}\n  Skills:"
            for skill in card.get("skills", []):
                skill_name = skill.get("name", "")
                skill_desc = skill.get("description", "")
                params = skill.get("parameters", {})
                params_str = ", ".join([f"{k}: {v}" for k, v in params.items()])
                agent_desc += f"\n    * {skill_name}: {skill_desc}"
                if params_str:
                    agent_desc += f"\n      Parameters: {params_str}"
            agents_info.append(agent_desc)
        
        agents_text = "\n".join(agents_info)
        
        prompt = f"""You are an intelligent assistant router. Analyze the user's query and determine which agent and skill should handle it.

CURRENT DATE/TIME CONTEXT:
- Today's date: {today}
- Tomorrow's date: {tomorrow}
- Current time: {current_time}

Available agents:
{agents_text}

User query: "{user_query}"

IMPORTANT: Extract ALL relevant parameters from the user's query:

For TASKS:
- For task creation: extract title, description, and priority (High/Medium/Low)
- For Chinese priority keywords: "高优先级"=High, "中优先级"=Medium, "低优先级"=Low
- For task listing: extract status filter (pending/completed) and priority filter
- For task operations: extract task_id if mentioned

For CALENDAR EVENTS:
- For event creation: MUST extract summary (title), start_time, end_time
- Time format: MUST use ISO 8601 format "YYYY-MM-DDTHH:MM:SS"
- Parse relative times using CURRENT DATE/TIME CONTEXT above:
  * "明天下午2点" = {tomorrow}T14:00:00
  * "今天上午10点" = {today}T10:00:00
  * "下午3点" = {today}T15:00:00
- Default duration: 1 hour if end_time not specified
- ALWAYS provide all three required fields: summary, start_time, end_time

For EMAILS:
- For listing emails: use list_emails with max_results parameter
- For reading specific email: use read_email with message_id or count parameter
- For sending email: extract to, subject, and body
- For searching: use search_emails with query parameter

Examples:
Query: "创建一个高优先级任务：review代码"
Response: {{"agent": "task_agent", "skill": "create_task", "params": {{"title": "review代码", "priority": "High"}}, "reasoning": "User wants to create a high priority task"}}

Query: "列出所有待办任务"
Response: {{"agent": "task_agent", "skill": "list_tasks", "params": {{"status": "pending"}}, "reasoning": "User wants to list pending tasks"}}

Query: "显示最新的5封邮件"
Response: {{"agent": "email_agent", "skill": "list_emails", "params": {{"max_results": 5}}, "reasoning": "User wants to see the latest 5 emails"}}

Query: "给john@example.com发送关于会议的邮件"
Response: {{"agent": "email_agent", "skill": "send_email", "params": {{"to": "john@example.com", "subject": "关于会议", "body": "会议相关内容"}}, "reasoning": "User wants to send an email about a meeting"}}

Query: "明天下午2点创建一个日历事件"
Response: {{"agent": "calendar_agent", "skill": "create_event", "params": {{"summary": "会议", "start_time": "{tomorrow}T14:00:00", "end_time": "{tomorrow}T15:00:00"}}, "reasoning": "User wants to create a calendar event tomorrow at 2 PM"}}

Query: "今天上午10点到11点半开会"
Response: {{"agent": "calendar_agent", "skill": "create_event", "params": {{"summary": "开会", "start_time": "{today}T10:00:00", "end_time": "{today}T11:30:00"}}, "reasoning": "User wants to create a meeting event today from 10:00 to 11:30"}}

Respond with ONLY a JSON object in this exact format (no markdown, no explanation):
{{
  "agent": "agent_name",
  "skill": "skill_name",
  "params": {{"param1": "value1", "param2": "value2"}},
  "reasoning": "brief explanation"
}}

If the query doesn't match any agent, use:
{{
  "agent": "none",
  "skill": "none",
  "params": {{}},
  "reasoning": "explanation"
}}"""

        messages = [
            {"role": "system", "content": "You are a precise JSON-only response assistant."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.chat_completion(messages, temperature=0.3, max_tokens=512)
            
            # Clean response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            import json
            intent = json.loads(response)
            
            return intent
        
        except Exception as e:
            print(f"Error parsing intent: {e}")
            return {
                "agent": "none",
                "skill": "none",
                "params": {},
                "reasoning": f"Error parsing intent: {str(e)}"
            }

# Made with Bob
