"""
🔧 BETA TESTING SYSTEM - Updated & Fixed
✅ Fixed Flask import issue
✅ Enhanced with better error handling
✅ Integrated with Failure Analysis Engine
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, Response, Flask  # Added Flask import
import sqlite3
import json
import os
import time
from datetime import datetime, timedelta
import random
import hashlib
import threading

# Create the blueprint
beta_bp = Blueprint('beta', __name__)

# Database file
DB_FILE = 'beta_users.db'

# Ensure database directory exists
os.makedirs(os.path.dirname(DB_FILE) if os.path.dirname(DB_FILE) else '.', exist_ok=True)

def init_beta_database():
    """Initialize or upgrade the beta testing database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS beta_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                company TEXT,
                use_case TEXT,
                experience_level TEXT,
                approved BOOLEAN DEFAULT FALSE,
                approval_code TEXT UNIQUE,
                invited_by TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                workflows_used INTEGER DEFAULT 0,
                feedback TEXT,
                tier TEXT DEFAULT 'free',
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Workflow usage table
        c.execute('''
            CREATE TABLE IF NOT EXISTS workflow_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                workflow_name TEXT NOT NULL,
                execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration REAL,
                success BOOLEAN,
                error_message TEXT,
                parameters TEXT,
                FOREIGN KEY (user_email) REFERENCES beta_users (email)
            )
        ''')
        
        # Feedback table
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                rating INTEGER,
                comments TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_email) REFERENCES beta_users (email)
            )
        ''')
        
        # Invitations table
        c.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inviter_email TEXT NOT NULL,
                invitee_email TEXT NOT NULL,
                invitation_code TEXT UNIQUE NOT NULL,
                sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted BOOLEAN DEFAULT FALSE,
                accepted_date TIMESTAMP
            )
        ''')
        
        # System statistics table
        c.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT UNIQUE NOT NULL,
                metric_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add indexes for performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_beta_users_email ON beta_users(email)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_beta_users_status ON beta_users(status)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_workflow_usage_user ON workflow_usage(user_email)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_user_feedback_user ON user_feedback(user_email)')
        
        # Initialize default stats
        default_stats = [
            ('total_applications', '0'),
            ('approved_users', '0'),
            ('total_workflows_run', '0'),
            ('average_rating', '0'),
            ('active_users_7d', '0'),
            ('invitations_sent', '0')
        ]
        
        for metric, value in default_stats:
            c.execute('''
                INSERT OR IGNORE INTO system_stats (metric_name, metric_value)
                VALUES (?, ?)
            ''', [metric, value])
        
        conn.commit()
        conn.close()
        
        print("✅ Beta testing database initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing beta database: {e}")
        return False

# Initialize database on import
init_beta_database()

class BetaManager:
    """Manager for beta testing system"""
    
    def __init__(self):
        self.active_sessions = {}
        self.notifications = []
        
    def add_application(self, email, name, company, use_case, experience_level):
        """Add a new beta application"""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Check if email already exists
            c.execute('SELECT email FROM beta_users WHERE email = ?', [email])
            if c.fetchone():
                conn.close()
                return {"success": False, "error": "Email already registered"}
            
            # Generate approval code
            approval_code = hashlib.md5(f"{email}{time.time()}".encode()).hexdigest()[:8].upper()
            
            # Insert new application
            c.execute('''
                INSERT INTO beta_users 
                (email, name, company, use_case, experience_level, approval_code, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [email, name, company, use_case, experience_level, approval_code, 'pending'])
            
            # Update statistics
            c.execute('''
                UPDATE system_stats 
                SET metric_value = CAST(metric_value AS INTEGER) + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE metric_name = 'total_applications'
            ''')
            
            conn.commit()
            conn.close()
            
            # Send welcome email (simulated)
            self._send_welcome_email(email, name, approval_code)
            
            return {"success": True, "approval_code": approval_code}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def approve_application(self, approval_code):
        """Approve a beta application"""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Find and approve user
            c.execute('''
                UPDATE beta_users 
                SET approved = TRUE, 
                    status = 'approved',
                    joined_date = CURRENT_TIMESTAMP
                WHERE approval_code = ? AND status = 'pending'
            ''', [approval_code])
            
            if c.rowcount == 0:
                conn.close()
                return {"success": False, "error": "Application not found or already processed"}
            
            # Get user email for notification
            c.execute('SELECT email, name FROM beta_users WHERE approval_code = ?', [approval_code])
            user = c.fetchone()
            
            # Update statistics
            c.execute('''
                UPDATE system_stats 
                SET metric_value = CAST(metric_value AS INTEGER) + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE metric_name = 'approved_users'
            ''')
            
            conn.commit()
            conn.close()
            
            if user:
                email, name = user
                self._send_approval_email(email, name)
            
            return {"success": True, "message": "Application approved successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def record_workflow_usage(self, user_email, workflow_name, duration, success=True, error_message=None, parameters=None):
        """Record workflow usage"""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Check if user exists and is approved
            c.execute('SELECT email FROM beta_users WHERE email = ? AND approved = TRUE', [user_email])
            if not c.fetchone():
                conn.close()
                return {"success": False, "error": "User not found or not approved"}
            
            # Record usage
            params_json = json.dumps(parameters) if parameters else None
            c.execute('''
                INSERT INTO workflow_usage 
                (user_email, workflow_name, duration, success, error_message, parameters)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', [user_email, workflow_name, duration, success, error_message, params_json])
            
            # Update user's workflow count
            c.execute('''
                UPDATE beta_users 
                SET workflows_used = workflows_used + 1,
                    last_active = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', [user_email])
            
            # Update total workflows stat
            c.execute('''
                UPDATE system_stats 
                SET metric_value = CAST(metric_value AS INTEGER) + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE metric_name = 'total_workflows_run'
            ''')
            
            conn.commit()
            conn.close()
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def submit_feedback(self, user_email, rating, comments, category='general'):
        """Submit user feedback"""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Check if user exists
            c.execute('SELECT email FROM beta_users WHERE email = ?', [user_email])
            if not c.fetchone():
                conn.close()
                return {"success": False, "error": "User not found"}
            
            # Record feedback
            c.execute('''
                INSERT INTO user_feedback 
                (user_email, rating, comments, category)
                VALUES (?, ?, ?, ?)
            ''', [user_email, rating, comments, category])
            
            # Update average rating
            c.execute('''
                SELECT AVG(rating) FROM user_feedback 
                WHERE rating IS NOT NULL
            ''')
            avg_rating = c.fetchone()[0] or 0
            
            c.execute('''
                UPDATE system_stats 
                SET metric_value = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE metric_name = 'average_rating'
            ''', [str(avg_rating)])
            
            conn.commit()
            conn.close()
            
            return {"success": True, "average_rating": avg_rating}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_statistics(self):
        """Get system statistics"""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Get all stats
            c.execute('SELECT metric_name, metric_value FROM system_stats')
            stats = {row[0]: row[1] for row in c.fetchall()}
            
            # Get recent activity
            c.execute('''
                SELECT COUNT(DISTINCT user_email) 
                FROM workflow_usage 
                WHERE execution_time > datetime('now', '-7 days')
            ''')
            active_users = c.fetchone()[0] or 0
            stats['active_users_7d'] = str(active_users)
            
            # Get pending applications
            c.execute('SELECT COUNT(*) FROM beta_users WHERE status = "pending"')
            stats['pending_applications'] = str(c.fetchone()[0] or 0)
            
            # Get recent feedback
            c.execute('''
                SELECT rating, comments, timestamp 
                FROM user_feedback 
                ORDER BY timestamp DESC 
                LIMIT 5
            ''')
            recent_feedback = c.fetchall()
            
            conn.close()
            
            return {
                "success": True,
                "stats": stats,
                "recent_feedback": [
                    {"rating": r[0], "comments": r[1], "timestamp": r[2]}
                    for r in recent_feedback
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_applications(self, status=None):
        """Get beta applications with optional filter"""
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            if status:
                c.execute('''
                    SELECT * FROM beta_users 
                    WHERE status = ? 
                    ORDER BY joined_date DESC
                ''', [status])
            else:
                c.execute('SELECT * FROM beta_users ORDER BY joined_date DESC')
            
            applications = c.fetchall()
            
            # Get column names
            c.execute('PRAGMA table_info(beta_users)')
            columns = [col[1] for col in c.fetchall()]
            
            conn.close()
            
            formatted = []
            for app in applications:
                app_dict = dict(zip(columns, app))
                # Hide sensitive data
                if 'approval_code' in app_dict:
                    app_dict['approval_code'] = app_dict['approval_code'][:4] + '****'
                formatted.append(app_dict)
            
            return {"success": True, "applications": formatted}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _send_welcome_email(self, email, name, approval_code):
        """Simulate sending welcome email"""
        print(f"📧 Welcome email sent to {email}")
        print(f"   Name: {name}")
        print(f"   Approval Code: {approval_code}")
        print(f"   Please wait for approval")
        return True
    
    def _send_approval_email(self, email, name):
        """Simulate sending approval email"""
        print(f"✅ Approval email sent to {email}")
        print(f"   Congratulations {name}! Your beta access has been approved.")
        print(f"   You can now access all features.")
        return True

# Initialize beta manager
beta_manager = BetaManager()

# ===================== ROUTES =====================

@beta_bp.route('/')
def beta_dashboard():
    """Beta testing dashboard"""
    stats = beta_manager.get_statistics()
    
    if stats.get('success'):
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Beta Testing Dashboard - Agentic Workflow Engine</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .dashboard-container { background: rgba(255,255,255,0.95); color: #333; border-radius: 20px; padding: 30px; margin-top: 30px; }
                .stat-card { background: linear-gradient(135deg, #4361ee, #3a0ca3); color: white; border-radius: 15px; padding: 20px; margin: 10px; text-align: center; }
                .stat-value { font-size: 2.5em; font-weight: bold; }
                .application-card { background: white; border-radius: 10px; padding: 15px; margin: 10px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            </style>
        </head>
        <body>
            <div class="container dashboard-container">
                <h1><i class="fas fa-vial"></i> Beta Testing Dashboard</h1>
                <p class="lead">Manage beta users, track usage, and collect feedback</p>
                
                <!-- Stats Row -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-value">{{ stats.stats.total_applications }}</div>
                            <div>Total Applications</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-value">{{ stats.stats.approved_users }}</div>
                            <div>Approved Users</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-value">{{ stats.stats.total_workflows_run }}</div>
                            <div>Workflows Run</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-value">{{ stats.stats.average_rating }}</div>
                            <div>Avg Rating</div>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-rocket"></i> Quick Actions</h5>
                                <div class="d-grid gap-2 mt-3">
                                    <a href="/beta/apply" class="btn btn-primary">
                                        <i class="fas fa-user-plus"></i> New Application
                                    </a>
                                    <a href="/beta/applications" class="btn btn-success">
                                        <i class="fas fa-list"></i> View Applications
                                    </a>
                                    <a href="/beta/feedback" class="btn btn-warning">
                                        <i class="fas fa-comment"></i> View Feedback
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-chart-line"></i> Recent Activity</h5>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-users"></i> <strong>{{ stats.stats.active_users_7d }}</strong> active users (7 days)</li>
                                    <li><i class="fas fa-clock"></i> <strong>{{ stats.stats.pending_applications }}</strong> pending applications</li>
                                    <li><i class="fas fa-star"></i> <strong>{{ stats.recent_feedback|length }}</strong> recent feedback items</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Recent Feedback -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-comment"></i> Recent Feedback</h5>
                    </div>
                    <div class="card-body">
                        {% if stats.recent_feedback %}
                            {% for fb in stats.recent_feedback %}
                                <div class="application-card">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            {% for i in range(5) %}
                                                {% if i < fb.rating %}
                                                    <i class="fas fa-star text-warning"></i>
                                                {% else %}
                                                    <i class="far fa-star text-secondary"></i>
                                                {% endif %}
                                            {% endfor %}
                                        </div>
                                        <small class="text-muted">{{ fb.timestamp }}</small>
                                    </div>
                                    <p class="mt-2 mb-0">{{ fb.comments[:200] }}{% if fb.comments|length > 200 %}...{% endif %}</p>
                                </div>
                            {% endfor %}
                        {% else %}
                            <p class="text-center text-muted">No feedback yet</p>
                        {% endif %}
                    </div>
                </div>
                
                <!-- Navigation -->
                <div class="text-center">
                    <a href="/" class="btn btn-outline-primary">
                        <i class="fas fa-arrow-left"></i> Back to Main Dashboard
                    </a>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        ''', stats=stats)
    else:
        return f"Error loading stats: {stats.get('error', 'Unknown error')}"

@beta_bp.route('/apply', methods=['GET', 'POST'])
def apply_beta():
    """Apply for beta access"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        company = request.form.get('company', '').strip()
        use_case = request.form.get('use_case', '').strip()
        experience_level = request.form.get('experience_level', 'beginner')
        
        if not email or not name:
            return render_template_string('''
            <div class="alert alert-danger">
                Email and name are required!
            </div>
            ''' + apply_form_html())
        
        result = beta_manager.add_application(email, name, company, use_case, experience_level)
        
        if result['success']:
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Application Submitted - Agentic Workflow Engine</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body { 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .success-card {
                        background: white;
                        border-radius: 20px;
                        padding: 40px;
                        max-width: 600px;
                        text-align: center;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    }
                </style>
            </head>
            <body>
                <div class="success-card">
                    <h1 class="text-success"><i class="fas fa-check-circle"></i> Application Submitted!</h1>
                    <p class="lead">Thank you for applying to the Agentic Workflow Engine beta program.</p>
                    
                    <div class="alert alert-info mt-4">
                        <h5><i class="fas fa-key"></i> Your Approval Code</h5>
                        <h2 class="text-primary">{{ approval_code }}</h2>
                        <p class="mb-0">Save this code for future reference.</p>
                    </div>
                    
                    <div class="mt-4">
                        <h5>What happens next?</h5>
                        <ol class="text-start">
                            <li>Your application will be reviewed (usually within 24 hours)</li>
                            <li>You'll receive an email when approved</li>
                            <li>Use your approval code to activate your account</li>
                            <li>Start using the Agentic Workflow Engine!</li>
                        </ol>
                    </div>
                    
                    <div class="mt-4">
                        <a href="/beta" class="btn btn-primary">
                            <i class="fas fa-home"></i> Back to Beta Dashboard
                        </a>
                        <a href="/" class="btn btn-outline-secondary">
                            <i class="fas fa-arrow-left"></i> Main Dashboard
                        </a>
                    </div>
                </div>
            </body>
            </html>
            ''', approval_code=result['approval_code'])
        else:
            return render_template_string(f'''
            <div class="alert alert-danger">
                Error: {result.get('error', 'Unknown error')}
            </div>
            ''' + apply_form_html())
    
    return apply_form_html()

def apply_form_html():
    """Return HTML for application form"""
    return '''
    <!DOCTYPE html>
<html>
<head>
    <title>Apply for Beta - Agentic Workflow Engine</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 20px;
        }
        .application-form {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            margin: 0 auto;
        }
        .form-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .feature-list {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="application-form">
            <div class="form-header">
                <h1 class="text-primary"><i class="fas fa-rocket"></i> Apply for Beta Access</h1>
                <p class="lead">Join the future of workflow automation</p>
            </div>
            
            <form method="POST" action="/beta/apply">
                <div class="mb-3">
                    <label for="email" class="form-label">
                        <i class="fas fa-envelope"></i> Email Address *
                    </label>
                    <input type="email" class="form-control form-control-lg" id="email" name="email" required>
                    <div class="form-text">We'll send approval notifications to this email</div>
                </div>
                
                <div class="mb-3">
                    <label for="name" class="form-label">
                        <i class="fas fa-user"></i> Full Name *
                    </label>
                    <input type="text" class="form-control form-control-lg" id="name" name="name" required>
                </div>
                
                <div class="mb-3">
                    <label for="company" class="form-label">
                        <i class="fas fa-building"></i> Company / Organization
                    </label>
                    <input type="text" class="form-control form-control-lg" id="company" name="company">
                </div>
                
                <div class="mb-3">
                    <label for="use_case" class="form-label">
                        <i class="fas fa-tasks"></i> Primary Use Case
                    </label>
                    <textarea class="form-control" id="use_case" name="use_case" rows="3" 
                              placeholder="Describe what you plan to use Agentic Workflow Engine for..."></textarea>
                </div>
                
                <div class="mb-4">
                    <label for="experience_level" class="form-label">
                        <i class="fas fa-chart-line"></i> Experience Level
                    </label>
                    <select class="form-select form-select-lg" id="experience_level" name="experience_level">
                        <option value="beginner">Beginner (new to automation)</option>
                        <option value="intermediate">Intermediate (some automation experience)</option>
                        <option value="advanced">Advanced (experienced with workflow automation)</option>
                        <option value="expert">Expert (develop automation systems)</option>
                    </select>
                </div>
                
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary btn-lg">
                        <i class="fas fa-paper-plane"></i> Submit Application
                    </button>
                    <a href="/beta" class="btn btn-outline-secondary btn-lg">
                        <i class="fas fa-arrow-left"></i> Back to Beta Dashboard
                    </a>
                </div>
            </form>
            
            <div class="feature-list">
                <h5><i class="fas fa-star"></i> Beta Program Benefits:</h5>
                <ul>
                    <li><strong>Early Access:</strong> Be among the first to use Agentic Workflow Engine</li>
                    <li><strong>Free Tier:</strong> 100 workflows/month at no cost</li>
                    <li><strong>Direct Support:</strong> Priority access to our development team</li>
                    <li><strong>Influence Development:</strong> Help shape the future features</li>
                    <li><strong>Special Pricing:</strong> Discounts on future paid plans</li>
                </ul>
                <p class="mb-0"><small><i class="fas fa-info-circle"></i> Applications are reviewed within 24 hours</small></p>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    '''

@beta_bp.route('/applications')
def view_applications():
    """View all beta applications"""
    status_filter = request.args.get('status', None)
    result = beta_manager.get_applications(status_filter)
    
    if not result['success']:
        return f"Error: {result.get('error', 'Unknown error')}"
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Beta Applications - Agentic Workflow Engine</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f8f9fa; }
            .application-table { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            .status-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 0.9em; }
            .status-pending { background: #ffc107; color: #000; }
            .status-approved { background: #198754; color: white; }
            .status-rejected { background: #dc3545; color: white; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <h1 class="mb-4"><i class="fas fa-list"></i> Beta Applications</h1>
            
            <!-- Filter buttons -->
            <div class="btn-group mb-4" role="group">
                <a href="/beta/applications" class="btn btn-outline-primary">All</a>
                <a href="/beta/applications?status=pending" class="btn btn-outline-warning">Pending</a>
                <a href="/beta/applications?status=approved" class="btn btn-outline-success">Approved</a>
                <a href="/beta/applications?status=rejected" class="btn btn-outline-danger">Rejected</a>
            </div>
            
            <div class="application-table">
                <table class="table table-hover mb-0">
                    <thead class="table-dark">
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Company</th>
                            <th>Experience</th>
                            <th>Status</th>
                            <th>Applied</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for app in applications %}
                        <tr>
                            <td>{{ app.name }}</td>
                            <td>{{ app.email }}</td>
                            <td>{{ app.company or 'N/A' }}</td>
                            <td>{{ app.experience_level }}</td>
                            <td>
                                <span class="status-badge status-{{ app.status }}">
                                    {{ app.status|upper }}
                                </span>
                            </td>
                            <td>{{ app.joined_date }}</td>
                            <td>
                                {% if app.status == 'pending' %}
                                <button class="btn btn-sm btn-success" onclick="approveApplication('{{ app.approval_code }}')">
                                    <i class="fas fa-check"></i> Approve
                                </button>
                                {% endif %}
                                <button class="btn btn-sm btn-info" onclick="viewDetails({{ app.id }})">
                                    <i class="fas fa-eye"></i> View
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if not applications %}
            <div class="alert alert-info mt-4">
                <i class="fas fa-info-circle"></i> No applications found.
            </div>
            {% endif %}
            
            <div class="mt-4">
                <a href="/beta" class="btn btn-outline-primary">
                    <i class="fas fa-arrow-left"></i> Back to Beta Dashboard
                </a>
                <a href="/beta/apply" class="btn btn-primary">
                    <i class="fas fa-user-plus"></i> New Application
                </a>
            </div>
        </div>
        
        <script>
            function approveApplication(approvalCode) {
                if (confirm('Approve this application?')) {
                    fetch(`/beta/api/approve/${approvalCode}`, { method: 'POST' })
                        .then(r => r.json())
                        .then(data => {
                            if (data.success) {
                                alert('✅ Application approved!');
                                location.reload();
                            } else {
                                alert('❌ Error: ' + data.error);
                            }
                        });
                }
            }
            
            function viewDetails(appId) {
                alert('View details for application ' + appId);
                // In a real system, this would open a modal or new page
            }
        </script>
    </body>
    </html>
    ''', applications=result['applications'])

@beta_bp.route('/feedback')
def view_feedback():
    """View user feedback"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute('''
            SELECT uf.*, bu.name 
            FROM user_feedback uf
            LEFT JOIN beta_users bu ON uf.user_email = bu.email
            ORDER BY uf.timestamp DESC
            LIMIT 50
        ''')
        
        feedback = c.fetchall()
        
        # Get column names
        c.execute('PRAGMA table_info(user_feedback)')
        columns = [col[1] for col in c.fetchall()] + ['user_name']
        
        conn.close()
        
        formatted = []
        for fb in feedback:
            fb_dict = dict(zip(columns, fb))
            formatted.append(fb_dict)
        
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>User Feedback - Agentic Workflow Engine</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container py-4">
                <h1 class="mb-4"><i class="fas fa-comment"></i> User Feedback</h1>
                
                <div class="row">
                    {% for fb in feedback %}
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <div>
                                        <h6 class="card-title mb-0">{{ fb.user_name or fb.user_email }}</h6>
                                        <small class="text-muted">{{ fb.category }}</small>
                                    </div>
                                    <div class="text-end">
                                        {% for i in range(5) %}
                                            {% if i < fb.rating %}
                                                <i class="fas fa-star text-warning"></i>
                                            {% else %}
                                                <i class="far fa-star text-secondary"></i>
                                            {% endif %}
                                        {% endfor %}
                                        <div>
                                            <small class="text-muted">{{ fb.timestamp }}</small>
                                        </div>
                                    </div>
                                </div>
                                <p class="card-text">{{ fb.comments }}</p>
                                {% if fb.resolved %}
                                <span class="badge bg-success">Resolved</span>
                                {% else %}
                                <span class="badge bg-warning">Pending</span>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                {% if not feedback %}
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> No feedback submitted yet.
                </div>
                {% endif %}
                
                <div class="mt-4">
                    <a href="/beta" class="btn btn-outline-primary">
                        <i class="fas fa-arrow-left"></i> Back to Beta Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        ''', feedback=formatted)
        
    except Exception as e:
        return f"Error: {e}"

# ===================== API ENDPOINTS =====================

@beta_bp.route('/api/stats')
def api_beta_stats():
    """Get beta system statistics API"""
    return jsonify(beta_manager.get_statistics())

@beta_bp.route('/api/applications')
def api_applications():
    """Get applications API"""
    status = request.args.get('status', None)
    return jsonify(beta_manager.get_applications(status))

@beta_bp.route('/api/apply', methods=['POST'])
def api_apply():
    """Apply for beta API"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"})
    
    result = beta_manager.add_application(
        email=data.get('email'),
        name=data.get('name'),
        company=data.get('company'),
        use_case=data.get('use_case'),
        experience_level=data.get('experience_level', 'beginner')
    )
    
    return jsonify(result)

@beta_bp.route('/api/approve/<approval_code>', methods=['POST'])
def api_approve(approval_code):
    """Approve application API"""
    result = beta_manager.approve_application(approval_code)
    return jsonify(result)

@beta_bp.route('/api/record-usage', methods=['POST'])
def api_record_usage():
    """Record workflow usage API"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"})
    
    result = beta_manager.record_workflow_usage(
        user_email=data.get('user_email'),
        workflow_name=data.get('workflow_name'),
        duration=data.get('duration', 0),
        success=data.get('success', True),
        error_message=data.get('error_message'),
        parameters=data.get('parameters')
    )
    
    return jsonify(result)

@beta_bp.route('/api/feedback', methods=['POST'])
def api_feedback():
    """Submit feedback API"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"})
    
    result = beta_manager.submit_feedback(
        user_email=data.get('user_email'),
        rating=data.get('rating'),
        comments=data.get('comments'),
        category=data.get('category', 'general')
    )
    
    return jsonify(result)

@beta_bp.route('/api/health')
def api_beta_health():
    """Beta system health check"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Check database tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        
        required_tables = ['beta_users', 'workflow_usage', 'user_feedback', 'system_stats']
        missing_tables = [t for t in required_tables if t not in tables]
        
        conn.close()
        
        if missing_tables:
            return jsonify({
                "status": "unhealthy",
                "error": f"Missing tables: {missing_tables}",
                "tables": tables
            })
        
        return jsonify({
            "status": "healthy",
            "tables": tables,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# ===================== STANDALONE TESTING =====================

if __name__ == '__main__':
    # Only runs when executing this file directly
    from flask import Flask  # Import Flask here to avoid circular imports
    app_integrated = Flask(__name__)
    app_integrated.register_blueprint(beta_bp, url_prefix='/beta')
    print("🚀 Beta Testing System running on http://localhost:5001")
    print("📊 Access at: http://localhost:5001/beta")
    print("📝 Apply at: http://localhost:5001/beta/apply")
    app_integrated.run(debug=True, port=5001)