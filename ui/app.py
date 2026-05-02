import streamlit as st
import requests
from datetime import datetime
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Page config
st.set_page_config(
    page_title="A2A 个人助手",
    page_icon="🤖",
    layout="wide"
)

# Orchestrator endpoint
ORCHESTRATOR_URL = "http://localhost:8000"

# Check DEMO_MODE
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

def check_orchestrator_health():
    """Check if orchestrator is available"""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_discovered_agents():
    """Get list of discovered agents"""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/agents", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get("agents", {})
        return {}
    except:
        return {}

def send_query(query: str):
    """Send query to orchestrator"""
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/query",
            json={"query": query},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error": "Request timed out. The agent might be processing a long task."
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Connection error: {str(e)}"
        }

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "orchestrator_online" not in st.session_state:
    st.session_state.orchestrator_online = check_orchestrator_health()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🤖 A2A 个人助手")
    st.markdown("*多智能体系统：邮件、日历和任务管理*")
with col2:
    if DEMO_MODE:
        st.markdown("### 🎭 演示模式")
        st.caption("使用模拟数据")

# Sidebar
with st.sidebar:
    st.header("系统状态")
    
    # Check orchestrator status
    if st.button("🔄 刷新状态"):
        st.session_state.orchestrator_online = check_orchestrator_health()
        st.rerun()
    
    if st.session_state.orchestrator_online:
        st.success("✅ 协调器在线")
        
        # Get discovered agents
        agents = get_discovered_agents()
        
        if agents:
            st.subheader("已发现的代理")
            for agent_name, agent_card in agents.items():
                with st.expander(f"📦 {agent_name}"):
                    st.write(f"**描述：** {agent_card.get('description', 'N/A')}")
                    st.write(f"**端点：** {agent_card.get('endpoint', 'N/A')}")
                    
                    skills = agent_card.get('skills', [])
                    if skills:
                        st.write("**技能：**")
                        for skill in skills:
                            st.write(f"- `{skill.get('name', 'N/A')}`")
        else:
            st.warning("⚠️ 未发现代理")
    else:
        st.error("❌ 协调器离线")
        st.info("请在端口 8000 启动协调器服务")
    
    st.divider()
    
    # Example queries
    st.subheader("💡 示例查询")
    examples = [
        "创建一个高优先级任务来审查提案",
        "今天的日程是什么？",
        "显示最新的 5 封邮件",
        "给 john@example.com 发送关于会议的邮件",
        "列出所有待办任务",
        "明天下午 2 点创建一个日历事件"
    ]
    
    for example in examples:
        if st.button(example, key=f"example_{example}", use_container_width=True):
            st.session_state.example_query = example
    
    st.divider()
    
    if st.button("🗑️ 清除聊天历史", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.subheader("💬 聊天")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show agent info for assistant messages
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]
            if metadata.get("agent_used"):
                st.caption(
                    f"🔧 代理：`{metadata['agent_used']}` | "
                    f"技能：`{metadata['skill_used']}`"
                )

# Handle example query from sidebar
if "example_query" in st.session_state:
    query = st.session_state.example_query
    del st.session_state.example_query
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Process query
    with st.chat_message("assistant"):
        with st.spinner("处理中..."):
            response = send_query(query)
            
            if response.get("status") == "ok":
                result = response.get("result", "无结果")
                st.markdown(result)
                
                # Store message with metadata
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result,
                    "metadata": {
                        "agent_used": response.get("agent_used"),
                        "skill_used": response.get("skill_used")
                    }
                })
                
                # Show agent info
                if response.get("agent_used"):
                    st.caption(
                        f"🔧 代理：`{response['agent_used']}` | "
                        f"技能：`{response['skill_used']}`"
                    )
            else:
                error_msg = f"❌ 错误：{response.get('error', '未知错误')}"
                st.error(error_msg)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
    
    st.rerun()

# Chat input
if prompt := st.chat_input("询问关于邮件、日历或任务的任何问题..."):
    if not st.session_state.orchestrator_online:
        st.error("❌ 协调器离线。请先启动服务。")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("处理中..."):
                response = send_query(prompt)
                
                if response.get("status") == "ok":
                    result = response.get("result", "无结果")
                    st.markdown(result)
                    
                    # Store message with metadata
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result,
                        "metadata": {
                            "agent_used": response.get("agent_used"),
                            "skill_used": response.get("skill_used")
                        }
                    })
                    
                    # Show agent info
                    if response.get("agent_used"):
                        st.caption(
                            f"🔧 代理：`{response['agent_used']}` | "
                            f"技能：`{response['skill_used']}`"
                        )
                else:
                    error_msg = f"❌ 错误：{response.get('error', '未知错误')}"
                    st.error(error_msg)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
        
        st.rerun()

# Footer
st.divider()
st.caption("A2A 个人助手 v1.0 | 基于 A2A 协议的多智能体系统")

# Made with Bob
