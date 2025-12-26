import os
import subprocess
import sys

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    packages = [
        "flask-cors",
        "pyautogui",
        "keyboard",
        "pillow",
        "opencv-python",
        "numpy"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ✅ {package}")
        except:
            print(f"  ❌ Failed to install {package}")
    
def create_missing_files():
    """Create missing module files"""
    print("\n📁 Creating missing module files...")
    
    # Desktop automation module
    desktop_content = '''import pyautogui
import keyboard
from flask import Blueprint, jsonify, request

desktop_bp = Blueprint('desktop', __name__)

@desktop_bp.route('/api/move', methods=['POST'])
def move_mouse():
    data = request.get_json()
    x = data.get('x', 0)
    y = data.get('y', 0)
    
    try:
        pyautogui.moveTo(x, y, duration=0.5)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@desktop_bp.route('/api/click', methods=['POST'])
def click_mouse():
    try:
        pyautogui.click()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@desktop_bp.route('/api/position')
def get_position():
    try:
        x, y = pyautogui.position()
        return jsonify({'success': True, 'x': x, 'y': y})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
'''
    
    # Teaching system module
    teaching_content = '''import json
import time
from flask import Blueprint, jsonify, request

teaching_bp = Blueprint('teaching', __name__)

class TeachingSystem:
    def __init__(self):
        self.recordings = []
    
    def record_action(self, action_type, data):
        self.recordings.append({
            'type': action_type,
            'data': data,
            'timestamp': time.time()
        })
    
    def save_workflow(self, name):
        workflow = {
            'name': name,
            'actions': self.recordings,
            'created_at': time.time()
        }
        return workflow

teaching = TeachingSystem()

@teaching_bp.route('/api/start', methods=['POST'])
def start_recording():
    teaching.recordings = []
    return jsonify({'success': True, 'message': 'Recording started'})

@teaching_bp.route('/api/stop', methods=['POST'])
def stop_recording():
    data = request.get_json()
    workflow = teaching.save_workflow(data.get('name', 'Unnamed'))
    return jsonify({'success': True, 'workflow': workflow})
'''
    
    with open('desktop_automation.py', 'w') as f:
        f.write(desktop_content)
        print("  ✅ Created desktop_automation.py")
    
    with open('teaching_system.py', 'w') as f:
        f.write(teaching_content)
        print("  ✅ Created teaching_system.py")

def fix_database():
    """Fix database schema"""
    print("\n🗄️  Fixing database schema...")
    
    import sqlite3
    from datetime import datetime
    
    try:
        # Backup old database
        if os.path.exists('beta_users.db'):
            import shutil
            shutil.copy2('beta_users.db', 'beta_users.db.backup')
            print("  ✅ Created backup: beta_users.db.backup")
        
        # Delete old database
        if os.path.exists('beta_users.db'):
            os.remove('beta_users.db')
            print("  ✅ Removed old database")
        
        # Create new database with correct schema
        conn = sqlite3.connect('beta_users.db')
        cursor = conn.cursor()
        
        # Create beta_users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS beta_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            company TEXT,
            use_case TEXT NOT NULL,
            details TEXT,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            invitation_code TEXT,
            last_login TIMESTAMP,
            workflow_count INTEGER DEFAULT 0
        )
        ''')
        
        # Create beta_stats table with correct schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS beta_stats (
            id INTEGER PRIMARY KEY,
            total_applications INTEGER DEFAULT 0,
            approved_users INTEGER DEFAULT 0,
            pending_review INTEGER DEFAULT 0,
            active_users INTEGER DEFAULT 0,
            last_updated TIMESTAMP
        )
        ''')
        
        # Initialize stats
        cursor.execute('''
        INSERT INTO beta_stats (total_applications, approved_users, 
                               pending_review, active_users, last_updated)
        VALUES (0, 0, 0, 0, ?)
        ''', (datetime.now(),))
        
        conn.commit()
        conn.close()
        print("  ✅ Database created with correct schema")
        
    except Exception as e:
        print(f"  ❌ Error fixing database: {e}")

def main():
    print("=" * 60)
    print("🔧 AGENTIC WORKFLOW ENGINE - FIX ALL ISSUES")
    print("=" * 60)
    
    install_dependencies()
    create_missing_files()
    fix_database()
    
    print("\n" + "=" * 60)
    print("✅ ALL FIXES COMPLETED!")
    print("=" * 60)
    print("\n🚀 Now you can run:")
    print("   cd D:\\agentic-core\\web")
    print("   python app.py")
    print("\n🌐 Access at: http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    main()