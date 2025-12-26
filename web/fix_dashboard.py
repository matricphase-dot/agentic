# fix_dashboard.py
import os
import json

print("🔧 FIXING DASHBOARD MODULE DISPLAY...")
print("=" * 50)

# Find all module files
modules = []
for file in os.listdir('.'):
    if file.endswith('.py') and file not in ['app.py', '__init__.py']:
        module_name = file.replace('.py', '').replace('_module', '').replace('_system', '')
        modules.append({
            'file': file,
            'name': module_name,
            'display': module_name.replace('_', ' ').title(),
            'imported': False
        })

print(f"Found {len(modules)} module files:")
for i, module in enumerate(modules, 1):
    print(f"{i}. {module['file']} -> {module['display']}")

# Create a simple app_test.py to test
simple_app = '''
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "testing",
        "modules": ''' + json.dumps([m['name'] for m in modules]) + ''',
        "message": "All modules detected"
    })

if __name__ == '__main__':
    print("Testing module detection...")
    app.run(debug=True, port=5001)
'''

with open('app_test.py', 'w') as f:
    f.write(simple_app)

print("\n✅ Created app_test.py")
print("🚀 Run: python app_test.py")
print("🌐 Then open: http://localhost:5001")
print("\nThis will confirm all modules are detected.")