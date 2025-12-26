"""
🔧 TESSERACT OCR INSTALLATION SCRIPT
🎯 For Agentic Workflow Engine - Week 17-18
"""

import os
import sys
import subprocess
import requests
import zipfile
import tempfile
from pathlib import Path

def install_tesseract_windows():
    """Install Tesseract OCR on Windows"""
    print("📥 Installing Tesseract OCR for Windows...")
    
    # Download URL for Tesseract installer
    url = "https://github.com/UB-Mannheim/tesseract/wiki/Downloads"
    print(f"Please download Tesseract from: {url}")
    print("\nManual installation steps:")
    print("1. Download the latest version (e.g., tesseract-ocr-w64-setup-5.3.3.20231005.exe)")
    print("2. Run the installer")
    print("3. Install to: C:\\Program Files\\Tesseract-OCR")
    print("4. Add to PATH during installation")
    print("\nAfter installation, restart your terminal and run:")
    print("python -c \"import pytesseract; print('Tesseract path:', pytesseract.get_tesseract_version())\"")
    
    # Alternative: Try to download directly
    try:
        print("\n⏳ Attempting automated download...")
        response = requests.get("https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe", 
                              stream=True, timeout=30)
        
        if response.status_code == 200:
            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, "tesseract_installer.exe")
            
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Download complete: {installer_path}")
            print(f"Please run the installer manually.")
            print(f"Then update computer_vision.py with:")
            print('pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"')
        else:
            print("⚠️  Could not download automatically. Please download manually.")
    except Exception as e:
        print(f"⚠️  Automated download failed: {e}")

def install_tesseract_linux():
    """Install Tesseract OCR on Linux"""
    print("📥 Installing Tesseract OCR for Linux...")
    
    try:
        # Check if apt is available (Ubuntu/Debian)
        subprocess.run(['apt-get', 'update'], check=True)
        subprocess.run(['apt-get', 'install', '-y', 'tesseract-ocr'], check=True)
        subprocess.run(['apt-get', 'install', '-y', 'libtesseract-dev'], check=True)
        print("✅ Tesseract OCR installed successfully!")
    except:
        try:
            # Try yum (CentOS/RHEL)
            subprocess.run(['yum', 'install', '-y', 'tesseract'], check=True)
            print("✅ Tesseract OCR installed successfully!")
        except:
            print("⚠️  Could not install Tesseract automatically.")
            print("Please install manually with:")
            print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
            print("  CentOS/RHEL: sudo yum install tesseract")

def install_tesseract_mac():
    """Install Tesseract OCR on macOS"""
    print("📥 Installing Tesseract OCR for macOS...")
    
    try:
        # Check if Homebrew is installed
        subprocess.run(['brew', '--version'], check=True, capture_output=True)
        print("✅ Homebrew found. Installing Tesseract...")
        subprocess.run(['brew', 'install', 'tesseract'], check=True)
        print("✅ Tesseract OCR installed successfully!")
    except:
        print("⚠️  Homebrew not found or installation failed.")
        print("Please install Homebrew first:")
        print("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("Then: brew install tesseract")

def check_tesseract_installation():
    """Check if Tesseract is installed"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR is already installed: {version}")
        return True
    except:
        print("❌ Tesseract OCR is not installed or not in PATH")
        return False

def main():
    """Main installation function"""
    print("=" * 60)
    print("🔧 TESSERACT OCR INSTALLATION FOR AGENTIC WORKFLOW ENGINE")
    print("🎯 Week 17-18: Computer Vision for UI Understanding")
    print("=" * 60)
    
    # Check current installation
    if check_tesseract_installation():
        print("\n✅ Tesseract is ready to use!")
        return
    
    # Determine OS and install
    if sys.platform == 'win32':
        install_tesseract_windows()
    elif sys.platform == 'linux':
        install_tesseract_linux()
    elif sys.platform == 'darwin':
        install_tesseract_mac()
    else:
        print(f"⚠️  Unsupported platform: {sys.platform}")
        print("Please install Tesseract OCR manually from:")
        print("https://github.com/tesseract-ocr/tesseract")
    
    print("\n📝 After installation, update computer_vision.py with:")
    print('pytesseract.pytesseract.tesseract_cmd = r"<path_to_tesseract>"')
    print("\n💡 For Windows, the default path is:")
    print('r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"')

if __name__ == "__main__":
    main()