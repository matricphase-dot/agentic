@echo off
echo 🚀 AGENTIC WORKFLOW ENGINE - WEEK 23-24 INSTALLATION
echo 🎯 Distributed Execution & Parallel Processing
echo.

cd /d "D:\agentic-core\web"

echo 📦 Installing distributed execution dependencies...
pip install requests==2.31.0

echo 📁 Creating distributed directories...
mkdir distributed_execution 2>nul
mkdir distributed_execution\task_logs 2>nul
mkdir distributed_execution\node_configs 2>nul

echo 🚀 Starting system with distributed execution...
echo.
echo 🌐 NEW ACCESS POINTS:
echo   1. Main Dashboard: http://localhost:5000
echo   2. Distributed Dashboard: http://localhost:5000/distributed
echo   3. Performance Dashboard: http://localhost:5000/performance
echo   4. Enhanced Automation: http://localhost:5000/automation
echo.
echo ⚡ DISTRIBUTED FEATURES:
echo   • Load balancing across multiple nodes
echo   • Parallel task execution
echo   • Fault tolerance with task reassignment
echo   • Real-time cluster monitoring
echo.
echo 🖥️  WORKER NODES:
echo   • Run worker_node.py on separate machines
echo   • Command: python worker_node.py --master http://YOUR_IP:5000
echo.
echo 🔧 Admin: admin / admin123
echo.

start http://localhost:5000/distributed
python app.py