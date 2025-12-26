@echo off
echo 📦 Installing Agentic Workflow Engine Dependencies...
echo.

cd /d "D:\agentic-core\web"

echo 🔧 Installing Core Dependencies...
pip install Flask==3.0.0
pip install Werkzeug==3.0.1
pip install Jinja2==3.1.3
pip install SQLAlchemy==2.0.23

echo 📊 Installing Data Analysis Dependencies...
pip install numpy==1.24.3
pip install pandas==2.1.4
pip install scikit-learn==1.3.0
pip install scipy==1.11.4

echo 🎨 Installing Visualization Dependencies...
pip install matplotlib==3.8.2
pip install seaborn==0.13.0

echo 🔍 Installing Computer Vision Dependencies...
pip install opencv-python==4.8.1.78
pip install Pillow==10.1.0
pip install pyautogui==0.9.54

echo ⚡ Installing Performance Dependencies...
pip install psutil==5.9.6
pip install cachetools==5.3.2

echo 🔗 Installing Utility Dependencies...
pip install python-dotenv==1.0.0
pip install requests==2.31.0
pip install schedule==1.2.0
pip install networkx==3.2.1
pip install tqdm==4.66.1

echo ✅ All dependencies installed successfully!
echo.
echo 🚀 To start the system: python app.py
pause