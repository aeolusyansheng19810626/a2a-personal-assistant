#!/bin/bash

echo "========================================"
echo "Starting A2A Personal Assistant"
echo "========================================"
echo ""

echo "Starting Task Agent (port 8003)..."
cd task_agent && uvicorn main:app --port 8003 &
TASK_PID=$!
cd ..
sleep 2

echo "Starting Calendar Agent (port 8002)..."
cd calendar_agent && uvicorn main:app --port 8002 &
CALENDAR_PID=$!
cd ..
sleep 2

echo "Starting Email Agent (port 8001)..."
cd email_agent && uvicorn main:app --port 8001 &
EMAIL_PID=$!
cd ..
sleep 2

echo "Starting Orchestrator (port 8000)..."
cd orchestrator && uvicorn main:app --port 8000 &
ORCH_PID=$!
cd ..
sleep 3

echo "Starting Streamlit UI (port 8501)..."
cd ui && streamlit run app.py &
UI_PID=$!
cd ..

echo ""
echo "========================================"
echo "All services started!"
echo "========================================"
echo ""
echo "Services:"
echo "- Task Agent:     http://localhost:8003 (PID: $TASK_PID)"
echo "- Calendar Agent: http://localhost:8002 (PID: $CALENDAR_PID)"
echo "- Email Agent:    http://localhost:8001 (PID: $EMAIL_PID)"
echo "- Orchestrator:   http://localhost:8000 (PID: $ORCH_PID)"
echo "- UI:             http://localhost:8501 (PID: $UI_PID)"
echo ""
echo "To stop all services, run:"
echo "kill $TASK_PID $CALENDAR_PID $EMAIL_PID $ORCH_PID $UI_PID"
echo ""
echo "Press Ctrl+C to exit..."

# Wait for user interrupt
wait

# Made with Bob
