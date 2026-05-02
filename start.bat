@echo off
echo ========================================
echo Starting A2A Personal Assistant
echo ========================================
echo.

echo Starting Task Agent (port 8003)...
start "Task Agent" cmd /k "cd task_agent && uvicorn main:app --port 8003"
timeout /t 2 /nobreak >nul

echo Starting Calendar Agent (port 8002)...
start "Calendar Agent" cmd /k "cd calendar_agent && uvicorn main:app --port 8002"
timeout /t 2 /nobreak >nul

echo Starting Email Agent (port 8001)...
start "Email Agent" cmd /k "cd email_agent && uvicorn main:app --port 8001"
timeout /t 2 /nobreak >nul

echo Starting Orchestrator (port 8000)...
start "Orchestrator" cmd /k "cd orchestrator && uvicorn main:app --port 8000"
timeout /t 3 /nobreak >nul

echo Starting Streamlit UI (port 8501)...
start "Streamlit UI" cmd /k "cd ui && streamlit run app.py"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Services:
echo - Task Agent:     http://localhost:8003
echo - Calendar Agent: http://localhost:8002
echo - Email Agent:    http://localhost:8001
echo - Orchestrator:   http://localhost:8000
echo - UI:             http://localhost:8501
echo.
echo Press any key to exit this window...
pause >nul

@REM Made with Bob
