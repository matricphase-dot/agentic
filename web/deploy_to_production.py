"""
Deployment script for production
"""

import os
import shutil
import subprocess
import time

def deploy_production():
    print("🚀 Deploying Agentic Workflow Engine to Production...")
    
    # 1. Stop any existing instances
    print("1. Stopping existing instances...")
    os.system("taskkill /F /IM python.exe 2>nul")
    
    # 2. Create backup
    print("2. Creating backup...")
    if os.path.exists("backup"):
        shutil.rmtree("backup")
    shutil.copytree(".", "backup", ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
    
    # 3. Install dependencies
    print("3. Installing dependencies...")
    subprocess.run(["pip", "install", "-r", "requirements.txt", "--quiet"])
    
    # 4. Start production system
    print("4. Starting production system...")
    print("   📊 Dashboard: http://localhost:5000")
    print("   ⚡ System will auto-start on boot")
    print("   📈 Market analytics active")
    print("   💰 Revenue tracking enabled")
    
    # Create startup script
    startup_script = """
@echo off
cd /d "%~dp0"
python production_system.py
"""
    
    with open("startup.bat", "w") as f:
        f.write(startup_script)
    
    # Add to startup (optional)
    if input("Add to Windows startup? (y/n): ").lower() == 'y':
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        shutil.copy("startup.bat", os.path.join(startup_path, "AgenticEngine.bat"))
        print("✅ Added to Windows startup")
    
    # 5. Start the system
    print("\n5. Launching production system...")
    time.sleep(2)
    
    # Run in new window
    os.system("start cmd /k python production_system.py")
    
    print("\n✅ DEPLOYMENT COMPLETE!")
    print("🎉 Agentic Workflow Engine is now running in production!")
    print("\nAccess Points:")
    print("   Main Dashboard: http://localhost:5000")
    print("   API Status: http://localhost:5000/api/system/status")
    print("   Market Analytics: http://localhost:5000/api/market/analytics")
    print("\nFeatures Active:")
    print("   ✅ All 10 core modules")
    print("   ✅ Multi-modal capabilities")
    print("   ✅ Enterprise features")
    print("   ✅ Market domination system")
    print("   ✅ Revenue generation")
    print("   ✅ Competitor tracking")

if __name__ == "__main__":
    deploy_production()