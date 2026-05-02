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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Orchestrator endpoint
ORCHESTRATOR_URL = "http://localhost:8000"

# Check DEMO_MODE
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# 初始化语言状态
if "lang" not in st.session_state:
    st.session_state.lang = "zh"

# 多语言翻译
i18n = {
    "zh": {
        "title": "A2A（Agent To Agent）个人助手",
        "subtitle": "多智能体系统：邮件、日历和任务管理",
        "brand_sub": "PERSONAL ASSISTANT",
        "system_status": "系统状态",
        "discovered_agents": "已发现的代理",
        "example_queries": "💡 示例查询",
        "refresh_status": "🔄 刷新",
        "clear_history": "🗑️ 清除聊天历史",
        "orchestrator_online": "🟢 协调器在线",
        "orchestrator_offline": "🔴 协调器离线",
        "orchestrator_offline_msg": "❌ 协调器离线。请先启动服务。",
        "task_agent": "任务代理",
        "calendar_agent": "日历代理",
        "email_agent": "邮件代理",
        "task_agent_desc": "基于 SQLite 的本地任务管理。创建、列出、完成和管理带优先级的任务。",
        "calendar_agent_desc": "Google Calendar 日历管理。列出、创建和管理日历事件。",
        "email_agent_desc": "Gmail 邮件管理。使用 Gmail API 读取、发送、搜索和列出邮件。",
        "description_label": "描述",
        "endpoint_label": "端点",
        "skills_label": "技能",
        "example_1": "创建一个高优先级任务来审查提案",
        "example_2": "今天的日程是什么？",
        "example_3": "显示最新的 5 封邮件",
        "example_4": "给 john@example.com 发送关于会议的邮件",
        "example_5": "列出所有待办任务",
        "example_6": "明天下午 2 点创建一个日历事件",
        "chat_input_placeholder": "询问关于邮件、日历或任务的任何问题...",
        "agent_label": "代理",
        "skill_label": "技能",
        "demo_mode": "演示模式",
    },
    "ja": {
        "title": "A2A（Agent To Agent）ﾊﾟｰｿﾅﾙｱｼｽﾀﾝﾄ",
        "subtitle": "ﾏﾙﾁｴｰｼﾞｪﾝﾄｼｽﾃﾑ：ﾒｰﾙ、ｶﾚﾝﾀﾞｰ、ﾀｽｸ管理",
        "brand_sub": "PERSONAL ASSISTANT",
        "system_status": "ｼｽﾃﾑｽﾃｰﾀｽ",
        "discovered_agents": "検出されたｴｰｼﾞｪﾝﾄ",
        "example_queries": "💡 ｻﾝﾌﾟﾙｸｴﾘ",
        "refresh_status": "🔄 更新",
        "clear_history": "🗑️ ﾁｬｯﾄ履歴をｸﾘｱ",
        "orchestrator_online": "🟢 ｵｰｹｽﾄﾚｰﾀｵﾝﾗｲﾝ",
        "orchestrator_offline": "🔴 ｵｰｹｽﾄﾚｰﾀｵﾌﾗｲﾝ",
        "orchestrator_offline_msg": "❌ ｵｰｹｽﾄﾚｰﾀがｵﾌﾗｲﾝです。ｻｰﾋﾞｽを起動してください。",
        "task_agent": "ﾀｽｸ ｴｰｼﾞｪﾝﾄ",
        "calendar_agent": "ｶﾚﾝﾀﾞｰ ｴｰｼﾞｪﾝﾄ",
        "email_agent": "ﾒｰﾙ ｴｰｼﾞｪﾝﾄ",
        "task_agent_desc": "SQLiteﾍﾞｰｽのﾛｰｶﾙﾀｽｸ管理。優先度付きﾀｽｸの作成・一覧・完了・管理。",
        "calendar_agent_desc": "Googleｶﾚﾝﾀﾞｰ管理。ｶﾚﾝﾀﾞｰｲﾍﾞﾝﾄの一覧・作成・管理。",
        "email_agent_desc": "Gmailﾒｰﾙ管理。Gmail APIでﾒｰﾙの読取・送信・検索・一覧表示。",
        "description_label": "説明",
        "endpoint_label": "ｴﾝﾄﾞﾎﾟｲﾝﾄ",
        "skills_label": "ｽｷﾙ",
        "example_1": "高優先度のﾀｽｸを作成してﾌﾟﾛﾎﾟｰｻﾙをﾚﾋﾞｭｰする",
        "example_2": "今日のｽｹｼﾞｭｰﾙは何ですか?",
        "example_3": "最新の5つのﾒｰﾙを表示",
        "example_4": "john@example.comに会議についてﾒｰﾙを送信",
        "example_5": "すべての待機中のﾀｽｸを列挙",
        "example_6": "明日の午後2時にｶﾚﾝﾀﾞｰｲﾍﾞﾝﾄを作成",
        "chat_input_placeholder": "ﾒｰﾙ、ｶﾚﾝﾀﾞｰ、ﾀｽｸについてのご質問...",
        "agent_label": "ｴｰｼﾞｪﾝﾄ",
        "skill_label": "ｽｷﾙ",
        "demo_mode": "ﾃﾞﾓﾓｰﾄﾞ",
    },
    "en": {
        "title": "A2A (Agent To Agent) Personal Assistant",
        "sidebar_title": "A2A (Agent To Agent) Personal Assistant",  # English sidebar with parentheses
        "subtitle": "Multi-Agent System: Email, Calendar & Task Management",
        "brand_sub": "PERSONAL ASSISTANT",
        "system_status": "System Status",
        "discovered_agents": "Discovered Agents",
        "example_queries": "💡 Example Queries",
        "refresh_status": "🔄 Refresh",
        "clear_history": "🗑️ Clear Chat History",
        "orchestrator_online": "🟢 Orchestrator Online",
        "orchestrator_offline": "🔴 Orchestrator Offline",
        "orchestrator_offline_msg": "❌ Orchestrator offline. Please start the service.",
        "task_agent": "Task Agent",
        "calendar_agent": "Calendar Agent",
        "email_agent": "Email Agent",
        "task_agent_desc": "SQLite-based local task management. Create, list, complete and manage prioritized tasks.",
        "calendar_agent_desc": "Google Calendar management. List, create and manage calendar events.",
        "email_agent_desc": "Gmail email management. Read, send, search and list emails using Gmail API.",
        "description_label": "Description",
        "endpoint_label": "Endpoint",
        "skills_label": "Skills",
        "example_1": "Create a high priority task to review the proposal",
        "example_2": "What's my schedule for today?",
        "example_3": "Show the latest 5 emails",
        "example_4": "Send an email to john@example.com about the meeting",
        "example_5": "List all pending tasks",
        "example_6": "Create a calendar event at 2 PM tomorrow",
        "chat_input_placeholder": "Ask any question about email, calendar, or tasks...",
        "agent_label": "Agent",
        "skill_label": "Skill",
        "demo_mode": "Demo Mode",
    }
}

def t(key):
    """获取当前语言的翻译"""
    lang = st.session_state.lang
    return i18n.get(lang, i18n["zh"]).get(key, key)

# ====== CSS Tokens & Styles ======
styles_css = """
/* ====== Tokens ====== */
:root {
  --bg:        #F7F7FB;
  --bg-2:      #EFEFF5;
  --surface:   #FFFFFF;
  --line:      #E8E8F0;
  --line-2:    #DEDEE8;
  --line-3:    #C9C9D6;
  --sidebar-bg:#F8F5FF;
  --fg:        #0F0F1A;
  --fg-2:      #2E2E40;
  --fg-3:      #5E5E73;
  --fg-4:      #9494A8;
  --brand:     #4338CA;
  --brand-2:   #6D28D9;
  --brand-3:   #8B5CF6;
  --brand-4:   #A78BFA;
  --accent:    #7C3AED;
  --accent-2:  #5B21B6;
  --electric:  #6366F1;
  --brand-50:  #F3F0FF;
  --brand-100: #E5DEFF;
  --brand-200: #C9BCFF;
  --brand-300: #A78BFA;
  --grad-1: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #A855F7 100%);
  --grad-2: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  --grad-aurora: linear-gradient(120deg, #4338CA 0%, #5B21B6 30%, #6D28D9 55%, #7C3AED 80%, #8B5CF6 100%);
  --grad-soft: linear-gradient(135deg, #F3F0FF 0%, #FAF5FF 100%);
  --green:     #10B981;
  --green-50:  #ECFDF5;
  --amber:     #F59E0B;
  --amber-50:  #FFFBEB;
  --rose:      #F43F5E;
  --rose-50:   #FFF1F2;
  --r-sm: 6px;
  --r-md: 10px;
  --r-lg: 14px;
  --r-xl: 18px;
  --shadow-sm: 0 1px 2px rgba(24,24,27,.04), 0 0 0 1px rgba(24,24,27,.04);
  --shadow-md: 0 4px 16px rgba(24,24,27,.06), 0 0 0 1px rgba(24,24,27,.05);
  --shadow-lg: 0 16px 40px rgba(24,24,27,.08), 0 0 0 1px rgba(24,24,27,.05);
}
* { box-sizing: border-box; }
body {
  font-family: "Inter","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  font-size: 14px; color: var(--fg); background: var(--bg);
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
}
button { font-family: inherit; cursor: pointer; }
input, textarea, select { font-family: inherit; font-size: inherit; color: inherit; }
.brand-title {
  font-size: 15px; font-weight: 700;
  background: var(--grad-aurora);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: .01em;
}
.brand-sub { font-size: 11px; color: var(--fg-4); margin-top: 2px; letter-spacing: .04em; text-transform: uppercase; }
.side-label { font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--fg-4); display: flex; align-items: center; gap: 8px; }
.foot-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 3px var(--green-50); }
.count-pill { display: inline-flex; align-items: center; justify-content: center; min-width: 18px; height: 18px; padding: 0 5px; background: var(--bg-2); color: var(--fg-3); font-size: 10.5px; font-weight: 600; border-radius: 999px; border: 1px solid var(--line-2); }
.page-title { color: #fff !important; font-size: 15px; margin: 0; }
.page-sub { color: rgba(255,255,255,.82) !important; font-size: 11.5px; margin-top: 1px; }
.status { background: rgba(255,255,255,.18) !important; border-color: rgba(255,255,255,.3) !important; color: #fff !important; backdrop-filter: blur(8px); padding: 4px 10px !important; font-size: 11px !important; }
.status-dot { background: #fff !important; box-shadow: 0 0 0 3px rgba(255,255,255,.25), 0 0 12px rgba(255,255,255,.6) !important; }

/* Custom Status Box for perfect alignment */
.custom-status-box {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 6px 12px !important;
  border-radius: var(--r-sm) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  height: 38px !important;
  min-height: 38px !important;
  max-height: 38px !important;
  line-height: 1 !important;
  width: 100% !important;
  margin: 0 !important;
  box-sizing: border-box !important;
  overflow: hidden !important;
  white-space: nowrap !important;
}
.status-online {
  background-color: #ecfdf5 !important;
  color: #065f46 !important;
  border: 1px solid #a7f3d0 !important;
}
.status-offline {
  background-color: #fef2f2 !important;
  color: #991b1b !important;
  border: 1px solid #fecaca !important;
}
.custom-status-box span.status-text {
  margin-top: 2px !important;
}
"""

streamlit_overrides = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');
html, body, [class*="css"], .stApp {
  font-family: "Inter","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif !important;
}
[data-testid="stApp"], .stApp { background: var(--bg) !important; }

/* 隐藏 Streamlit 顶部菜单/页脚 */
#MainMenu, footer { visibility: hidden; height: 0; }
header[data-testid="stHeader"] { height: 0 !important; min-height: 0 !important; background: transparent !important; box-shadow: none !important; overflow: visible !important; }
.stAppDeployButton { display: none !important; }

/* 侧边栏展开按钮 */
[data-testid="stSidebarExpandButton"],
[data-testid="stSidebarCollapseButton"] {
  z-index: 9999999 !important;
  color: #0F0F1A !important;
  background-color: rgba(255, 255, 255, 0.8) !important;
  border-radius: 50% !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
  margin-top: 8px !important;
  margin-left: 8px !important;
}
[data-testid="stSidebarExpandButton"]:hover,
[data-testid="stSidebarCollapseButton"]:hover {
  background-color: white !important;
}
[data-testid="stSidebarCollapsedControl"] {
  z-index: 9999998 !important;
}

/* 主区域边距 */
.block-container {
  padding-top: 64px !important;
  padding-bottom: 120px !important;
  padding-left: 32px !important;
  padding-right: 32px !important;
  max-width: 100% !important;
  margin: 0 !important;
}

/* ================= Sidebar ================= */
section[data-testid="stSidebar"][aria-expanded="true"] {
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--line);
  width: 300px !important;
  min-width: 300px !important;
}
.brand {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 300px !important;
  height: 60px !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 0 1.5rem !important;
  border-bottom: 1px solid var(--line) !important;
  background: var(--sidebar-bg) !important;
  box-sizing: border-box !important;
  z-index: 1000 !important;
  margin: 0 !important;
}

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
  align-items: center !important;
}
section[data-testid="stSidebar"] [data-testid="column"] {
  margin: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="column"] > div {
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  height: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="column"] [data-testid="stVerticalBlock"] {
  gap: 0 !important;
  padding: 0 !important;
}
section[data-testid="stSidebar"] .stButton, 
section[data-testid="stSidebar"] .stMarkdown {
  margin-bottom: 0 !important;
  margin-top: 0 !important;
  padding: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="column"] [data-testid="stMarkdownContainer"] {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1 !important;
  height: 38px !important;
}
section[data-testid="stSidebar"] [data-testid="column"] [data-testid="stMarkdownContainer"] p {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1 !important;
  height: 38px !important;
  display: flex !important;
  align-items: center !important;
}
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
  margin-bottom: 0 !important;
}

section[data-testid="stSidebar"] .stButton {
  display: flex;
  justify-content: flex-end;
}
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
  background: linear-gradient(135deg, var(--brand-50), var(--brand-100)) !important;
  border: 1px solid var(--brand-200) !important;
  border-radius: 8px !important;
  color: var(--accent-2) !important;
  padding: 10px 12px !important;
  height: auto !important;
  min-height: 36px !important;
  font-size: 13.5px !important;
  transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] button[kind="secondary"] p,
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] p {
  font-size: 13.5px !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover,
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
  background: linear-gradient(135deg, var(--brand-100), var(--brand-200)) !important;
  color: var(--accent) !important;
  border-color: var(--accent) !important;
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2) !important;
  transform: translateY(-2px);
}

section[data-testid="stSidebar"] [data-baseweb="input"] > div,
section[data-testid="stSidebar"] [data-baseweb="textarea"] > div,
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: var(--r-sm) !important;
  font-size: 11px !important;
  color: var(--fg) !important;
  box-shadow: none !important;
  min-height: 34px !important;
}
section[data-testid="stSidebar"] [data-baseweb="input"] > div:focus-within,
section[data-testid="stSidebar"] [data-baseweb="textarea"] > div:focus-within,
section[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--brand-3) !important;
  box-shadow: 0 0 0 3px var(--brand-50) !important;
}
[data-baseweb="select"] input {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}
section[data-testid="stSidebar"] label {
  font-size: 11px !important; color: var(--fg-3) !important; font-weight: 500 !important;
  margin-bottom: 4px !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  width: 100%;
  background: var(--grad-1) !important;
  background-size: 150% 150% !important;
  color: #fff !important;
  border: 0 !important;
  border-radius: var(--r-sm) !important;
  height: 38px !important;
  min-height: 38px !important;
  margin: 0 !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 0 4px !important;
  white-space: nowrap !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: 0 6px 16px rgba(124,58,237,.28), inset 0 1px 0 rgba(255,255,255,.18) !important;
  transition: background-position .3s, transform .05s, box-shadow .2s !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p {
  font-size: 13px !important;
  white-space: nowrap !important;
  margin: 0 !important;
  line-height: 1 !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background-position: 100% 0 !important;
  box-shadow: 0 10px 22px rgba(124,58,237,.35) !important;
}

/* 侧边栏 alert 组件完美对齐 */
section[data-testid="stSidebar"] [data-testid="stAlert"] { 
  font-size: 13px !important; 
  height: 38px !important;
  min-height: 38px !important;
  margin: 0 !important;
  padding: 0 12px !important; 
  white-space: nowrap !important; 
  display: flex !important;
  align-items: center !important;
}
section[data-testid="stSidebar"] [data-testid="stAlert"] * { font-size: 13px !important; white-space: nowrap !important; margin: 0 !important; }
section[data-testid="stSidebar"] [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  line-height: 1 !important;
  margin: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stAlert"] div { font-size: 13px !important; }
section[data-testid="stSidebar"] [data-testid="stAlert"] span { font-size: 13px !important; }
section[data-testid="stSidebar"] .stAlert { font-size: 13px !important; }
section[data-testid="stSidebar"] .stAlert * { font-size: 13px !important; }
section[data-testid="stSidebar"] .stAlert > * { font-size: 13px !important; }
/* 确保列内的 alert 也被应用 */
[data-testid="stHorizontalBlock"] [data-testid="stAlert"] { 
  font-size: 13px !important; 
  height: 38px !important;
  min-height: 38px !important;
  margin: 0 !important;
  padding: 0 12px !important; 
  white-space: nowrap !important; 
  display: flex !important;
  align-items: center !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stAlert"] * { font-size: 13px !important; white-space: nowrap !important; margin: 0 !important; }

/* 侧边栏 Expander (卡片) 组件字号 */
section[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
section[data-testid="stSidebar"] [data-testid="stExpander"] summary span,
section[data-testid="stSidebar"] [data-testid="stExpander"] summary div {
  font-size: 13.5px !important;
  font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stText"],
section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] li,
section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] span,
section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong {
  font-size: 13px !important;
  line-height: 1.6 !important;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] code {
  font-size: 12px !important;
}
/* Hide default Streamlit expander chevron SVG in sidebar - multiple selectors for HF compat */
section[data-testid="stSidebar"] [data-testid="stExpander"] summary svg,
section[data-testid="stSidebar"] details summary svg,
section[data-testid="stSidebar"] .streamlit-expanderHeader svg,
section[data-testid="stSidebar"] details > summary > svg {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
}

/* ================= 主区顶部 Topbar ================= */
.topbar-wrapper {
  width: 100% !important;
  height: 60px !important;
}
.topbar-wrapper .topbar {
  position: fixed !important;
  top: 0 !important;
  left: 300px !important;
  right: 0 !important;
  height: 60px !important;
  padding: 0 32px !important;
  z-index: 1000 !important;
  background: var(--grad-aurora) !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
}
@media (max-width: 768px) {
  .topbar-wrapper .topbar { left: 0 !important; }
}
[data-testid="stSidebar"][aria-expanded="false"] ~ div .topbar-wrapper .topbar {
  left: 0 !important;
}
[data-testid="stSidebar"][aria-expanded="false"] .brand {
  transform: translateX(-300px) !important;
  opacity: 0 !important;
}

.topbar-left { display: flex; flex-direction: column; }
.page-title { font-size: 15px !important; font-weight: 600 !important; color: white !important; margin-bottom: 2px !important; }
.page-sub { font-size: 11px !important; color: rgba(255,255,255,0.8) !important; }
.topbar-right { display: flex !important; align-items: center !important; gap: 12px !important; padding-right: 80px !important; }
.status { display: inline-flex !important; align-items: center !important; gap: 6px !important; padding: 6px 12px !important; border: 1px solid rgba(255,255,255,.3) !important; border-radius: 999px !important; color: white !important; font-size: 11px !important; white-space: nowrap !important; }
.demo-pill { margin-right: 0 !important; }
.status-dot { display: inline-flex !important; width: 6px !important; height: 6px !important; border-radius: 50% !important; background: white !important; flex-shrink: 0 !important; }

/* ================= 语言切换器 ================= */
div[data-testid="stPopover"] {
  position: fixed !important;
  top: 16px !important;
  right: 32px !important;
  left: auto !important;
  width: auto !important;
  z-index: 1001 !important;
}
div[data-testid="stPopover"] button {
  display: inline-flex !important; align-items: center !important; gap: 6px !important;
  height: 28px !important; padding: 0 8px 0 9px !important;
  background: rgba(255,255,255,.18) !important;
  border: 1px solid rgba(255,255,255,.3) !important;
  border-radius: 999px !important;
  color: white !important;
  font-size: 11.5px !important; font-weight: 500 !important;
  backdrop-filter: blur(8px) !important;
  min-height: 28px !important;
  box-shadow: none !important;
  transition: background .15s, border-color .15s;
}
div[data-testid="stPopover"] button:hover {
  background: rgba(255,255,255,.28) !important;
  border-color: rgba(255,255,255,.45) !important;
}
div[data-testid="stPopover"] button p {
  font-size: 11.5px !important; font-weight: 500 !important; margin: 0 !important;
  font-variant-numeric: tabular-nums; letter-spacing: .02em; min-width: 14px; text-align: center;
}
div[data-testid="stPopoverBody"] {
  min-width: 172px !important;
  max-width: 210px !important;
  background: #fff !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
  box-shadow: 0 16px 40px rgba(15,15,26,.18), 0 2px 6px rgba(15,15,26,.08) !important;
  padding: 0 !important;
  overflow: hidden !important;
}
div[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] {
  gap: 2px !important; padding: 4px !important;
}
.lang-hdr {
  font-size: 12.5px !important; font-weight: 600; letter-spacing: .06em;
  text-transform: uppercase; color: var(--fg-4);
  white-space: nowrap;
  padding: 8px 12px 6px; margin: 0;
  border-bottom: 1px solid var(--line);
}
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"]:has(.lang-hdr) {
  margin: 0 -4px !important; padding: 0 !important;
}
div[data-testid="stPopoverBody"] button {
  display: flex !important; align-items: center !important; gap: 8px !important;
  width: 100% !important; padding: 7px 10px !important;
  background: transparent !important; border: 0 !important; border-radius: 6px !important;
  color: var(--fg) !important; font-size: 12.5px !important; justify-content: flex-start !important;
  min-height: 0 !important; height: auto !important;
  text-align: left !important;
}
div[data-testid="stPopoverBody"] button:hover { background: var(--bg-2) !important; color: var(--fg) !important; border-color: transparent !important; }
div[data-testid="stPopoverBody"] [data-testid="baseButton-primary"],
div[data-testid="stPopoverBody"] button[kind="primary"] {
  background: var(--brand-50) !important;
  color: var(--accent) !important;
  font-weight: 600 !important;
}
div[data-testid="stPopoverBody"] [data-testid="baseButton-primary"]:hover,
div[data-testid="stPopoverBody"] button[kind="primary"]:hover {
  background: var(--brand-100) !important;
}
div[data-testid="stPopoverBody"] button p { margin: 0 !important; width: 100%; font-size: 12.5px !important; }

/* ================= 对话气泡 ================= */
.msg-hook { display: none !important; }

[data-testid="stChatMessage"] {
  background: transparent !important;
  padding: 0 !important;
  margin-bottom: 24px !important;
  display: flex !important;
  width: 100% !important;
  gap: 16px !important;
  align-items: flex-start !important;
}

/* User Message */
[data-testid="stChatMessage"]:has(.msg-user) {
  flex-direction: row-reverse !important;
  justify-content: flex-start !important;
  align-items: center !important;
}
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] {
  background: linear-gradient(135deg, #4F46E5, #7C3AED, #A855F7) !important;
  color: #fff !important;
  border-radius: 14px !important;
  border-top-right-radius: 4px !important;
  padding: 14px 18px !important;
  max-width: 75% !important;
  width: fit-content !important;
  flex: none !important;
  box-shadow: 0 10px 28px rgba(124,58,237,.32) !important;
  border: none !important;
  margin-left: auto !important;
  margin-right: 0 !important;
  align-self: center !important;
}
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] p { color: #fff !important; margin: 0 !important;}
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] [data-testid="stVerticalBlock"] {
  gap: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] .stMarkdown {
  margin: 0 !important;
  padding: 0 !important;
}

/* Assistant Message */
[data-testid="stChatMessage"]:has(.msg-assistant) {
  justify-content: flex-start !important;
}
[data-testid="stChatMessage"]:has(.msg-assistant) [data-testid="stChatMessageContent"] {
  background: #FFFFFF !important;
  border: 1px solid #E8E8F0 !important;
  border-radius: 14px !important;
  border-top-left-radius: 4px !important;
  padding: 16px 20px !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.04) !important;
  position: relative !important;
  overflow: visible !important;
  flex: 1 !important;
}
[data-testid="stChatMessage"]:has(.msg-assistant) [data-testid="stChatMessageContent"]::before {
  content: "" !important;
  position: absolute !important;
  left: -1px !important; top: -1px !important; bottom: -1px !important; width: 4px !important;
  background: linear-gradient(180deg, #4F46E5, #7C3AED, #A855F7) !important;
  border-radius: 14px 0 0 4px !important;
}

/* Avatars */
[data-testid="stChatMessage"] > div:first-child {
  width: 36px !important; height: 36px !important; min-width: 36px !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  color: transparent !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}
[data-testid="stChatMessage"] > div:first-child * {
  display: none !important;
}

[data-testid="stChatMessage"]:has(.msg-user) > div:first-child {
  align-self: center !important;
  margin-top: auto !important;
  margin-bottom: auto !important;
  background-color: #F3F4F6 !important;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%234B5563'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'/%3E%3C/svg%3E") !important;
  background-size: 20px !important; background-position: center !important; background-repeat: no-repeat !important;
  border: 1px solid #E5E7EB !important;
}

[data-testid="stChatMessage"]:has(.msg-assistant) > div:first-child {
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z'/%3E%3C/svg%3E") center / 20px no-repeat, linear-gradient(135deg, #8B5CF6, #7C3AED) !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.4) !important;
}

/* ================= Chat Input ================= */
[data-testid="stChatInput"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}
/* Move border/radius to inner flex row so overflow:hidden clips the abs-positioned button */
[data-testid="stChatInput"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: 16px !important;
  box-shadow: 0 12px 32px rgba(124,58,237,.08), 0 0 0 1px rgba(124,58,237,.04) !important;
  padding: 4px 6px 4px 12px !important;
  position: relative !important;
  overflow: hidden !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  margin: 0 !important;
}
[data-testid="stChatInput"] textarea {
  font-size: 14px !important;
  color: var(--fg) !important;
  padding: 8px 0 !important;
}
/* Chat submit button - circle, sits at right edge inside the container */
[data-testid="stChatInputSubmitButton"],
[data-testid="stChatInputSubmitButton"] button {
  background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
  border-radius: 50% !important;
  border: none !important;
  width: 36px !important; height: 36px !important;
  min-width: 36px !important; min-height: 36px !important;
  max-width: 36px !important; max-height: 36px !important;
  padding: 0 !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  cursor: pointer !important;
  flex-shrink: 0 !important;
  align-self: center !important;
}
[data-testid="stChatInputSubmitButton"] svg { fill: white !important; width: 16px !important; height: 16px !important; }
"""

st.markdown(f"<style>\n{styles_css}\n{streamlit_overrides}\n</style>", unsafe_allow_html=True)

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

if "agents_cache" not in st.session_state:
    st.session_state.agents_cache = get_discovered_agents()

# Topbar
agent_count = len(st.session_state.agents_cache)
demo_pill_html = f'<div class="status demo-pill">🎬 {t("demo_mode")}</div>' if DEMO_MODE else ""

topbar_html = f"<div class='topbar-wrapper'><div class='topbar'><div class='topbar-left'><div class='page-title'>{t('title')}</div><div class='page-sub'>{t('subtitle')}</div></div><div class='topbar-right'>" + demo_pill_html + "<div id='lang-switcher-anchor'></div></div></div></div></div>"
st.markdown(topbar_html, unsafe_allow_html=True)

# Language Switcher - positioned in topbar via CSS (position:fixed)
lang_labels = {"zh": "中", "ja": "日", "en": "英"}
cur_label = lang_labels.get(st.session_state.lang, "中")
with st.popover(cur_label, use_container_width=False):
    st.markdown('<p class="lang-hdr">LANGUAGE / 语言</p>', unsafe_allow_html=True)
    for code, abbr, name in [("zh", "CN", "简体中文"), ("ja", "JP", "日本語"), ("en", "EN", "English")]:
        active = st.session_state.lang == code
        label = f"{abbr}  {name}  ✓" if active else f"{abbr}  {name}"
        if st.button(label, use_container_width=True,
                     type="primary" if active else "secondary",
                     key=f"lang_{code}"):
            st.session_state.lang = code
            st.rerun()

# Sidebar
with st.sidebar:
    # Sidebar title: English without parentheses, others with parentheses
    sidebar_title = t('sidebar_title') if st.session_state.lang == "en" else t('title')
    if st.session_state.lang == "en":
        # For English: A2A (Agent To Agent) on first line, Personal Assistant on second line
        brand_html = '<div class="brand"><div class="brand-text"><span class="brand-title">A2A (Agent To Agent)<br>Personal Assistant</span></div></div>'
    else:
        brand_sub = t('brand_sub')
        brand_html = f'<div class="brand"><div class="brand-text"><span class="brand-title">{sidebar_title}</span><span class="brand-sub">{brand_sub}</span></div></div>'
    st.markdown(brand_html, unsafe_allow_html=True)

    st.markdown(f'<div class="side-label">{t("system_status")}</div>', unsafe_allow_html=True)

    # Check orchestrator status - status on left, refresh button on right
    col1, col2 = st.columns([1.8, 1], gap="small")
    with col1:
        if st.session_state.orchestrator_online:
            msg = t("orchestrator_online")
            emoji = msg[0]
            text = msg[1:].strip()
            st.markdown(f'<div class="custom-status-box status-online"><span>{emoji}</span><span class="status-text">{text}</span></div>', unsafe_allow_html=True)
        else:
            msg = t("orchestrator_offline")
            emoji = msg[0]
            text = msg[1:].strip()
            st.markdown(f'<div class="custom-status-box status-offline"><span>{emoji}</span><span class="status-text">{text}</span></div>', unsafe_allow_html=True)

    with col2:
        if st.button(t("refresh_status"), use_container_width=True, type="primary"):
            st.session_state.orchestrator_online = check_orchestrator_health()
            st.session_state.agents_cache = get_discovered_agents()
            st.rerun()

    if st.session_state.orchestrator_online:
        # Get agents from cache
        agents = st.session_state.agents_cache

        if agents:
            st.markdown(f'<div class="side-label">{t("discovered_agents")} <span class="count-pill">{len(agents)}</span></div>', unsafe_allow_html=True)
            for agent_name, agent_card in agents.items():
                display_name = t(agent_name)
                with st.expander(f"📦 {display_name}"):
                    desc_key = f"{agent_name}_desc"
                    description = t(desc_key) if t(desc_key) != desc_key else agent_card.get('description', 'N/A')
                    st.write(f"**{t('description_label')}：** {description}")
                    st.write(f"**{t('endpoint_label')}：** {agent_card.get('endpoint', 'N/A')}")

                    skills = agent_card.get('skills', [])
                    if skills:
                        st.write(f"**{t('skills_label')}：**")
                        for skill in skills:
                            st.write(f"- `{skill.get('name', 'N/A')}`")
        else:
            st.warning("⚠️ 未发现代理")
    else:
        st.info("请在端口 8000 启动协调器服务")

    st.divider()

    # Example queries
    st.markdown(f'<div class="side-label">{t("example_queries")}</div>', unsafe_allow_html=True)
    example_keys = ["example_1", "example_2", "example_3", "example_4", "example_5", "example_6"]

    for key in example_keys:
        example_text = t(key)
        if st.button(example_text, key=f"btn_{key}", use_container_width=True):
            st.session_state.example_query = example_text

    st.divider()

    if st.button(t("clear_history"), use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f'<span class="msg-hook msg-user"></span>{message["content"]}', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="✨"):
            st.markdown('<span class="msg-hook msg-assistant"></span>', unsafe_allow_html=True)
            st.markdown(message["content"])

            # Show agent info for assistant messages
            if "metadata" in message:
                metadata = message["metadata"]
                if metadata.get("agent_used"):
                    st.caption(
                        f"🔧 {t('agent_label')}: `{metadata['agent_used']}` | "
                        f"{t('skill_label')}: `{metadata['skill_used']}`"
                    )

# Handle example query from sidebar
if "example_query" in st.session_state:
    query = st.session_state.example_query
    del st.session_state.example_query

    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})

    # Display user message
    with st.chat_message("user"):
        st.markdown(f'<span class="msg-hook msg-user"></span>{query}', unsafe_allow_html=True)

    # Process query
    with st.chat_message("assistant", avatar="✨"):
        st.markdown('<span class="msg-hook msg-assistant"></span>', unsafe_allow_html=True)
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
if prompt := st.chat_input(t("chat_input_placeholder")):
    if not st.session_state.orchestrator_online:
        st.error(t("orchestrator_offline_msg"))
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(f'<span class="msg-hook msg-user"></span>{prompt}', unsafe_allow_html=True)

        # Process query
        with st.chat_message("assistant", avatar="✨"):
            st.markdown('<span class="msg-hook msg-assistant"></span>', unsafe_allow_html=True)
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

st.markdown("""
<div style="position:fixed; bottom:108px; left:0; right:0; text-align:center; color: #9CA3AF; font-size: 12px; pointer-events: none; z-index: 9999;">
  <span style="pointer-events: auto;">
    Built by <a href="https://github.com/aeolusyansheng19810626" target="_blank" style="color: var(--violet); text-decoration: none;">Sheng Yan</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/aeolusyansheng19810626" target="_blank" style="color: var(--violet); text-decoration: none;">GitHub</a>
  </span>
</div>
""", unsafe_allow_html=True)
