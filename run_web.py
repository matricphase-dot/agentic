#!/usr/bin/env python
"""
Run the web interface
"""
import subprocess
import sys
import os

print("="*60)
print("Starting Agentic Workflow Engine Web Interface")
print("="*60)

# Check if in correct directory
if not os.path.exists("web/app.py"):
    print("❌ Error: web/app.py not found")
    print("Please run this script from D:\agentic-core\")
    sys.exit(1)

# Install dependencies if needed
try:
    import flask
except ImportError:
    print("Installing Flask...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

# Run the app
print("\n🚀 Launching web interface...")
print("📊 Open: http://localhost:5000")
print("Press Ctrl+C to stop\n")

os.chdir("web")
subprocess.run([sys.executable, "app.py"])
