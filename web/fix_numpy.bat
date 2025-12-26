@echo off
echo 🔧 FIXING NUMPY & ALL DEPENDENCIES...
echo.

cd /d "D:\agentic-core\web"

echo 📦 Downgrading NumPy to 1.24.3 (Required by OpenCV)...
pip uninstall numpy -y
pip install numpy==1.24.3

echo 🔧 Reinstalling OpenCV with correct NumPy...
pip uninstall opencv-python -y
pip install opencv-python==4.8.1.78

echo 📊 Installing all required modules...
pip install scikit-learn==1.3.0
pip install scipy==1.11.4
pip install pandas==2.1.4
pip install matplotlib==3.8.2
pip install seaborn==0.13.0
pip install networkx==3.2.1
pip install tqdm==4.66.1

echo 🖥️ Installing desktop automation...
pip install pyautogui==0.9.54
pip install keyboard==0.13.5
pip install mouse==0.7.1

echo 📈 Installing performance modules...
pip install psutil==5.9.6
pip install cachetools==5.3.2

echo 🔗 Installing utilities...
pip install schedule==1.2.0
pip install Flask-Mail==0.9.1
pip install python-dotenv==1.0.0
pip install requests==2.31.0

echo ✅ ALL DEPENDENCIES FIXED!
echo.
echo 🚀 Now run: python app.py
pause