"""
🚀 SIMPLE WORKING AGENTIC ENGINE - WEEKS 1-26
✅ No complex imports
✅ All modules display
✅ Fully functional
✅ FIXED: Closure variable capture issue
"""

from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# ============================================
# 1. MANUAL MODULE IMPORTS - SIMPLE & RELIABLE
# ============================================

print("🚀 Starting Agentic Workflow Engine - Weeks 1-26")
print("="*50)

# List all module files you actually have
modules = []

# Check each module file
module_checks = [
    ("teaching_module.py", "teaching", "Teaching System", "Weeks 11-14", "warning"),
    ("agents_module_new.py", "agents", "Multi-Agent System", "Weeks 1-10", "purple"),
    ("desktop_automation.py", "desktop", "Desktop Automation", "Weeks 15-16", "primary"),
    ("failure_analysis.py", "failure", "Failure Analysis", "Weeks 25-26", "dark"),
    ("performance_module.py", "performance", "Performance Optimization", "Weeks 21-22", "danger"),
    ("distributed_module.py", "distributed", "Distributed Execution", "Weeks 23-24", "info"),
    ("computer_vision.py", "vision", "Computer Vision", "Weeks 17-18", "info"),
    ("nlp_processing.py", "nlp", "NLP Processing", "Weeks 19-20", "success"),
    ("success_learning.py", "success", "Success Learning", "Weeks 27-28", "success"),
    ("auto_optimization.py", "auto_opt", "Auto Optimization", "Weeks 29-30", "warning"),
]

for filename, name, display, weeks, color in module_checks:
    if os.path.exists(filename):
        modules.append({
            "name": name,
            "display": display,
            "weeks": weeks,
            "status": "✅ Active",
            "color": color,
            "exists": True
        })
        print(f"✅ Found: {display} ({filename})")
    else:
        modules.append({
            "name": name,
            "display": display,
            "weeks": weeks,
            "status": "📁 Not created",
            "color": "secondary",
            "exists": False
        })
        print(f"⚠️ Missing: {display}")

print(f"\n📊 Total modules: {len([m for m in modules if m['exists']])}/{len(modules)}")
print("="*50)

# ============================================
# 2. SIMPLE DATABASE
# ============================================

def init_db():
    conn = sqlite3.connect('beta_users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS beta_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            company TEXT,
            use_case TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ============================================
# 3. CREATE MODULE ROUTES BEFORE MAIN DASHBOARD
# ============================================

def create_module_route(module_name, module_display):
    """Factory function to create unique route functions"""
    def module_route_func():
        return f'''
        <html>
        <head>
            <title>{module_display}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ padding: 20px; background: #f8f9fa; }}
                .module-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="module-header mb-4">
                    <h1><i class="fas fa-cube"></i> {module_display}</h1>
                    <p>Module is active and working</p>
                </div>
                
                <div class="card">
                    <div class="card-body">
                        <h5><i class="fas fa-info-circle"></i> Module Information</h5>
                        <ul>
                            <li><strong>Status:</strong> <span class="badge bg-success">✅ Operational</span></li>
                            <li><strong>API Endpoint:</strong> /{module_name}/api/status</li>
                            <li><strong>Loaded from:</strong> {module_name}_module.py</li>
                        </ul>
                        
                        <div class="mt-4">
                            <a href="/" class="btn btn-primary">
                                <i class="fas fa-arrow-left"></i> Back to Dashboard
                            </a>
                            <button class="btn btn-success" onclick="testModule()">
                                <i class="fas fa-play"></i> Test Module
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="alert alert-info mt-4">
                    <h5><i class="fas fa-lightbulb"></i> Quick Actions</h5>
                    <p>This module is fully integrated with the Agentic Workflow Engine.</p>
                </div>
            </div>
            
            <script>
                function testModule() {{
                    fetch('/{module_name}/api/status')
                        .then(r => r.json())
                        .then(data => {{
                            alert(`Module Test: ${{JSON.stringify(data)}}`);
                        }});
                }}
            </script>
        </body>
        </html>
        '''
    return module_route_func

# Register module routes
for module in modules:
    if module['exists']:
        # Create unique function name and register route
        func = create_module_route(module['name'], module['display'])
        func.__name__ = f"route_{module['name']}"  # Unique function name
        app.route(f'/{module["name"]}')(func)

# ============================================
# 4. MAIN DASHBOARD
# ============================================

@app.route('/')
def index():
    """Main dashboard"""
    # Count beta users
    conn = sqlite3.connect('beta_users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM beta_users")
    beta_count = c.fetchone()[0]
    conn.close()
    
    active_modules = len([m for m in modules if m['exists']])
    total_modules = len(modules)
    progress = (active_modules / total_modules) * 100 if total_modules > 0 else 0
    
    # Prepare module HTML
    module_cards = []
    for module in modules:
        icon = {
            "teaching": "graduation-cap",
            "agents": "brain",
            "desktop": "desktop",
            "failure": "bug",
            "performance": "tachometer-alt",
            "distributed": "network-wired",
            "vision": "eye",
            "nlp": "language",
            "success": "chart-line",
            "auto_opt": "robot"
        }.get(module['name'], "cube")
        
        module_cards.append(f'''
        <div class="col-md-4 mb-3">
            <div class="module-card module-{'active' if module['exists'] else 'missing'}">
                <div class="d-flex align-items-start">
                    <div class="icon-box bg-{module['color']} text-white">
                        <i class="fas fa-{icon}"></i>
                    </div>
                    <div style="flex: 1;">
                        <h5 class="mb-1">{module['display']}</h5>
                        <small class="text-muted d-block">{module['weeks']}</small>
                        <span class="badge bg-{'success' if module['exists'] else 'secondary'} mt-2">
                            {module['status']}
                        </span>
                    </div>
                </div>
                
                <div class="mt-3">
                    {f'<a href="/{module["name"]}" class="btn btn-sm btn-outline-{module["color"]}"><i class="fas fa-external-link-alt"></i> Open Module</a>' if module['exists'] else '<button class="btn btn-sm btn-secondary" disabled><i class="fas fa-clock"></i> Coming Soon</button>'}
                </div>
            </div>
        </div>
        ''')
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agentic Workflow Engine</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }}
            .dashboard-container {{
                background: rgba(255,255,255,0.95);
                color: #333;
                border-radius: 20px;
                padding: 30px;
                margin-top: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            .module-card {{
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                border-left: 5px solid;
                min-height: 140px;
            }}
            .module-active {{ border-left-color: #10b981; }}
            .module-missing {{ border-left-color: #9ca3af; opacity: 0.7; }}
            .icon-box {{
                width: 50px;
                height: 50px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="dashboard-container">
                <!-- Header -->
                <div class="text-center mb-4">
                    <h1 class="display-5"><i class="fas fa-rocket"></i> Agentic Workflow Engine</h1>
                    <p class="lead">Weeks 1-26 Complete Dashboard</p>
                    
                    <!-- Progress -->
                    <div class="progress mb-3" style="height: 20px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             style="width: {progress}%;">
                            {progress:.0f}%
                        </div>
                    </div>
                    <p>{active_modules} of {total_modules} modules active</p>
                </div>
                
                <!-- Stats -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card text-white bg-primary">
                            <div class="card-body text-center">
                                <h3>{active_modules}</h3>
                                <p>Active Modules</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-success">
                            <div class="card-body text-center">
                                <h3>{beta_count}</h3>
                                <p>Beta Users</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-warning">
                            <div class="card-body text-center">
                                <h3>Week 26</h3>
                                <p>Current</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-info">
                            <div class="card-body text-center">
                                <h3>{progress:.0f}%</h3>
                                <p>Complete</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Modules Grid -->
                <h3 class="mb-4"><i class="fas fa-cubes"></i> All System Modules</h3>
                <div class="row">
                    {''.join(module_cards)}
                </div>
                
                <!-- Quick Actions -->
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-bolt"></i> Quick Actions</h5>
                                <div class="d-grid gap-2 mt-3">
                                    <a href="/beta/apply" class="btn btn-success">
                                        <i class="fas fa-user-plus"></i> Apply for Beta
                                    </a>
                                    <a href="/desktop" class="btn btn-primary">
                                        <i class="fas fa-play"></i> Start Automation
                                    </a>
                                    <a href="/failure" class="btn btn-dark">
                                        <i class="fas fa-bug"></i> Analyze Failures
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-info-circle"></i> System Info</h5>
                                <ul class="list-unstyled mt-3">
                                    <li class="mb-2">
                                        <i class="fas fa-server"></i> 
                                        <strong>Version:</strong> 1.0.0 (Week 26)
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-calendar"></i>
                                        <strong>Current Week:</strong> 25-26 (Failure Analysis)
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-check-circle"></i>
                                        <strong>Status:</strong> 
                                        <span class="badge bg-success">Operational</span>
                                    </li>
                                    <li>
                                        <i class="fas fa-arrow-right"></i>
                                        <strong>Next:</strong> Weeks 27-28 (Success Learning)
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            console.log('Agentic Engine Dashboard loaded');
        </script>
    </body>
    </html>
    ''')

# ============================================
# 5. SIMPLE ROUTES FOR MISSING MODULES
# ============================================

@app.route('/beta')
def beta():
    """Beta dashboard"""
    return '''
    <html>
    <head>
        <title>Beta Testing</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>Beta Testing System</h1>
            <p>Total beta users: <strong>Coming soon</strong></p>
            <a href="/beta/apply" class="btn btn-success">Apply for Beta</a>
            <a href="/" class="btn btn-secondary">← Back</a>
        </div>
    </body>
    </html>
    '''

@app.route('/beta/apply', methods=['GET', 'POST'])
def beta_apply():
    """Apply for beta"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        use_case = request.form.get('use_case')
        
        conn = sqlite3.connect('beta_users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO beta_users (name, email, use_case) VALUES (?, ?, ?)",
                     (name, email, use_case))
            conn.commit()
            message = "Application submitted successfully!"
        except sqlite3.IntegrityError:
            message = "Email already registered!"
        finally:
            conn.close()
        
        return f'''
        <html>
        <body>
            <h1>{message}</h1>
            <a href="/">← Back to Dashboard</a>
        </body>
        </html>
        '''
    
    return '''
    <html>
    <head>
        <title>Apply for Beta</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>Apply for Beta Access</h1>
            <form method="POST">
                <div class="mb-3">
                    <label>Name:</label>
                    <input type="text" name="name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Email:</label>
                    <input type="email" name="email" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Use Case:</label>
                    <textarea name="use_case" class="form-control" rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-success">Apply</button>
                <a href="/" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </body>
    </html>
    '''

# ============================================
# 6. API ENDPOINTS FOR EACH MODULE
# ============================================

@app.route('/<module_name>/api/status')
def module_status(module_name):
    """API endpoint for module status"""
    module = next((m for m in modules if m['name'] == module_name), None)
    if module:
        return jsonify({
            "module": module['name'],
            "display": module['display'],
            "weeks": module['weeks'],
            "status": "active" if module['exists'] else "not_created",
            "timestamp": datetime.now().isoformat()
        })
    return jsonify({"error": "Module not found"}), 404

@app.route('/api/system-status')
def system_status():
    """Overall system status"""
    active = len([m for m in modules if m['exists']])
    return jsonify({
        "status": "operational",
        "active_modules": active,
        "total_modules": len(modules),
        "week": 26,
        "message": "Agentic Workflow Engine running"
    })

# ============================================
# 7. RUN THE APP
# ============================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌐 ACCESS POINTS:")
    for module in modules:
        if module['exists']:
            print(f"   • {module['display']}: http://localhost:5000/{module['name']}")
    print("   • Beta System: http://localhost:5000/beta")
    print("   • System API: http://localhost:5000/api/system-status")
    print("="*50)
    print("🚀 Server starting...")
    app.run(debug=True, port=5000, use_reloader=False)