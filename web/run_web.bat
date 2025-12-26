@echo off
echo Starting Agentic Workflow Engine Web Interface...
echo.

D:
cd D:\agentic-core\web

echo Installing dependencies...
pip install flask flask-socketio plotly pandas eventlet

echo.
echo Starting web server...
echo Dashboard: http://localhost:5000
echo.

python app.py

pause