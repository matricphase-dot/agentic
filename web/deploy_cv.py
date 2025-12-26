"""
🚀 DEPLOYMENT SCRIPT FOR COMPUTER VISION INTEGRATION
🎯 Agentic Workflow Engine - Week 17-18
"""

import os
import sys
import subprocess
import time

def print_step(step, description):
    """Print a deployment step"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {description}")
    print(f"{'='*60}")

def run_command(command, check=True):
    """Run a shell command"""
    print(f"$ {command}")
    try:
        if check:
            subprocess.run(command, shell=True, check=True)
        else:
            subprocess.run(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Command failed: {e}")
        return False
    return True

def main():
    """Main deployment function"""
    print("🚀 AGENTIC WORKFLOW ENGINE - COMPUTER VISION DEPLOYMENT")
    print("📅 Week 17-18: UI Understanding with OpenCV & Tesseract")
    print("=" * 60)
    
    # Step 1: Install Python dependencies
    print_step(1, "Installing Python Dependencies")
    dependencies = [
        "opencv-python==4.8.1.78",
        "numpy==1.24.3",
        "pytesseract==0.3.10",
        "Pillow==10.1.0",
        "Flask==3.0.0",
        "pyautogui==0.9.54"
    ]
    
    for dep in dependencies:
        run_command(f"pip install {dep}")
    
    # Step 2: Create necessary directories
    print_step(2, "Creating Directories")
    directories = [
        "cv_screenshots",
        "cv_templates", 
        "cv_results",
        "cv_workflows",
        "uploads"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    # Step 3: Check Tesseract installation
    print_step(3, "Checking Tesseract OCR Installation")
    try:
        import pytesseract
        print("✅ pytesseract module is installed")
        
        # Try to find Tesseract
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract found: {version}")
        except:
            print("⚠️  Tesseract executable not found in PATH")
            print("\n💡 For Windows users:")
            print("1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("2. Install to: C:\\Program Files\\Tesseract-OCR")
            print("3. Update computer_vision.py with:")
            print('   pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"')
            
            # Offer to run installation script
            response = input("\nRun Tesseract installation helper? (y/n): ")
            if response.lower() == 'y':
                run_command("python install_tesseract.py")
    except ImportError:
        print("❌ pytesseract not installed. Installing...")
        run_command("pip install pytesseract")
    
    # Step 4: Verify OpenCV installation
    print_step(4, "Verifying OpenCV Installation")
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV not installed. Installing...")
        run_command("pip install opencv-python-headless")
    
    # Step 5: Initialize database
    print_step(5, "Initializing Database")
    run_command("python -c \"from app import init_db; init_db()\"", check=False)
    
    # Step 6: Test the system
    print_step(6, "Testing System Components")
    
    print("\n🔍 Testing imports:")
    test_imports = [
        "import cv2",
        "import pytesseract", 
        "import pyautogui",
        "import numpy as np",
        "from PIL import ImageGrab"
    ]
    
    for import_stmt in test_imports:
        try:
            exec(import_stmt)
            print(f"✅ {import_stmt}")
        except ImportError as e:
            print(f"❌ {import_stmt} - {e}")
    
    # Step 7: Run the application
    print_step(7, "Starting Agentic Workflow Engine")
    print("\n🎯 DEPLOYMENT COMPLETE!")
    print("\n🌐 Access Points:")
    print("  • Main Dashboard: http://localhost:5000")
    print("  • Computer Vision: http://localhost:5000/cv")
    print("  • Desktop Control: http://localhost:5000/desktop")
    print("  • Beta Testing:   http://localhost:5000/beta")
    print("\n🔧 Admin Login:")
    print("  • Username: admin")
    print("  • Password: admin123")
    print("\n🚀 Starting application...")
    
    # Ask to start the application
    response = input("\nStart the application now? (y/n): ")
    if response.lower() == 'y':
        print("\nStarting Flask server... Press Ctrl+C to stop")
        run_command("python app.py", check=False)

if __name__ == "__main__":
    main()