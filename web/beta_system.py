"""
COMPLETE BETA TESTING SYSTEM
"""
import sqlite3
import json
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template_string

beta_bp = Blueprint('beta', __name__, url_prefix='/beta')

# Database setup
def init_beta_db():
    conn = sqlite3.connect('beta_users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS beta_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        company TEXT,
        use_case TEXT,
        status TEXT DEFAULT 'pending',
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approved_at TIMESTAMP,
        rejection_reason TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS beta_stats (
        id INTEGER PRIMARY KEY,
        total_users INTEGER DEFAULT 0,
        approved_users INTEGER DEFAULT 0,
        pending_users INTEGER DEFAULT 0,
        last_updated TIMESTAMP
    )
    ''')
    
    # Initialize stats if empty
    cursor.execute("SELECT COUNT(*) FROM beta_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO beta_stats (total_users, approved_users, pending_users, last_updated) VALUES (0, 0, 0, ?)", 
                      (datetime.now(),))
    
    conn.commit()
    conn.close()

# Initialize database
init_beta_db()

@beta_bp.route('/')
def beta_home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Beta Testing - Agentic Workflow Engine</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                width: 100%;
                background: white;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            .header {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.8rem;
                margin-bottom: 10px;
                font-weight: 800;
            }
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0;
            }
            .left-panel {
                padding: 40px;
                background: #f8fafc;
            }
            .right-panel {
                padding: 40px;
                background: white;
            }
            .form-group {
                margin-bottom: 25px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #334155;
                font-size: 0.95rem;
            }
            .form-group input,
            .form-group textarea,
            .form-group select {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 1rem;
                transition: all 0.3s;
            }
            .form-group input:focus,
            .form-group textarea:focus,
            .form-group select:focus {
                outline: none;
                border-color: #4f46e5;
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            }
            .btn {
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                width: 100%;
                text-align: center;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
            }
            .features {
                margin-top: 30px;
            }
            .feature {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                padding: 15px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }
            .feature-icon {
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                margin-right: 15px;
            }
            .feature-text h3 {
                font-size: 1rem;
                color: #334155;
                margin-bottom: 5px;
            }
            .feature-text p {
                font-size: 0.9rem;
                color: #64748b;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 30px;
            }
            .stat-box {
                background: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }
            .stat-number {
                font-size: 2rem;
                font-weight: 800;
                color: #4f46e5;
                display: block;
            }
            .stat-label {
                font-size: 0.9rem;
                color: #64748b;
                margin-top: 5px;
            }
            .nav {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
            }
            .nav a {
                text-decoration: none;
                color: #4f46e5;
                font-weight: 600;
                padding: 10px 20px;
                border-radius: 8px;
                transition: all 0.3s;
            }
            .nav a:hover {
                background: rgba(79, 70, 229, 0.1);
            }
            .success-message {
                background: #10b981;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                display: none;
            }
            @media (max-width: 768px) {
                .content {
                    grid-template-columns: 1fr;
                }
                .stats {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Join Our Beta Program</h1>
                <p>Be among the first to experience the future of AI automation</p>
            </div>
            
            <div class="content">
                <div class="left-panel">
                    <h2 style="margin-bottom: 25px; color: #334155;">Apply for Beta Access</h2>
                    
                    <form id="betaForm">
                        <div class="form-group">
                            <label for="email">Email Address *</label>
                            <input type="email" id="email" name="email" required placeholder="you@company.com">
                        </div>
                        
                        <div class="form-group">
                            <label for="name">Full Name *</label>
                            <input type="text" id="name" name="name" required placeholder="John Doe">
                        </div>
                        
                        <div class="form-group">
                            <label for="company">Company / Organization</label>
                            <input type="text" id="company" name="company" placeholder="Optional">
                        </div>
                        
                        <div class="form-group">
                            <label for="use_case">How do you plan to use Agentic Workflow Engine? *</label>
                            <select id="use_case" name="use_case" required>
                                <option value="">Select your use case</option>
                                <option value="automation">Business Process Automation</option>
                                <option value="development">Software Development</option>
                                <option value="data">Data Analysis & Reporting</option>
                                <option value="research">Research & Analysis</option>
                                <option value="testing">QA & Testing Automation</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="details">Tell us more about your use case</label>
                            <textarea id="details" name="details" rows="4" placeholder="Describe what you want to automate..."></textarea>
                        </div>
                        
                        <button type="submit" class="btn">Apply for Beta Access</button>
                    </form>
                    
                    <div id="successMessage" class="success-message">
                        ✅ Application submitted successfully! We'll contact you within 48 hours.
                    </div>
                    
                    <div class="nav">
                        <a href="/">← Back to Dashboard</a>
                        <a href="/beta/dashboard">Admin Dashboard</a>
                    </div>
                </div>
                
                <div class="right-panel">
                    <h2 style="margin-bottom: 25px; color: #334155;">Why Join the Beta?</h2>
                    
                    <div class="features">
                        <div class="feature">
                            <div class="feature-icon">🚀</div>
                            <div class="feature-text">
                                <h3>Early Access</h3>
                                <p>Get exclusive access to new features before public release</p>
                            </div>
                        </div>
                        
                        <div class="feature">
                            <div class="feature-icon">💰</div>
                            <div class="feature-text">
                                <h3>Free Pro Tier</h3>
                                <p>6 months of Pro plan ($29/month value) for all beta testers</p>
                            </div>
                        </div>
                        
                        <div class="feature">
                            <div class="feature-icon">🤝</div>
                            <div class="feature-text">
                                <h3>Direct Influence</h3>
                                <p>Shape product development with your feedback</p>
                            </div>
                        </div>
                        
                        <div class="feature">
                            <div class="feature-icon">🎁</div>
                            <div class="feature-text">
                                <h3>Beta Bonuses</h3>
                                <p>Special rewards and recognition for top testers</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <span class="stat-number" id="totalUsers">0</span>
                            <span class="stat-label">Total Applicants</span>
                        </div>
                        
                        <div class="stat-box">
                            <span class="stat-number" id="approvedUsers">0</span>
                            <span class="stat-label">Approved Users</span>
                        </div>
                        
                        <div class="stat-box">
                            <span class="stat-number" id="pendingUsers">0</span>
                            <span class="stat-label">Pending Review</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Load stats
            async function loadStats() {
                try {
                    const response = await fetch('/beta/api/stats');
                    const data = await response.json();
                    
                    document.getElementById('totalUsers').textContent = data.total_users || 0;
                    document.getElementById('approvedUsers').textContent = data.approved_users || 0;
                    document.getElementById('pendingUsers').textContent = data.pending_users || 0;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }
            
            // Handle form submission
            document.getElementById('betaForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = {
                    email: document.getElementById('email').value,
                    name: document.getElementById('name').value,
                    company: document.getElementById('company').value,
                    use_case: document.getElementById('use_case').value,
                    details: document.getElementById('details').value
                };
                
                try {
                    const response = await fetch('/beta/api/apply', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        // Show success message
                        document.getElementById('successMessage').style.display = 'block';
                        document.getElementById('betaForm').reset();
                        
                        // Scroll to success message
                        document.getElementById('successMessage').scrollIntoView({ behavior: 'smooth' });
                        
                        // Reload stats
                        loadStats();
                    } else {
                        alert('Error: ' + result.message);
                    }
                } catch (error) {
                    alert('Error submitting application. Please try again.');
                }
            });
            
            // Load stats on page load
            loadStats();
        </script>
    </body>
    </html>
    '''

@beta_bp.route('/dashboard')
def beta_dashboard():
    """Admin dashboard for managing beta applications"""
    conn = sqlite3.connect('beta_users.db')
    cursor = conn.cursor()
    
    # Get all applications
    cursor.execute('''
    SELECT id, email, name, company, use_case, status, 
           strftime('%Y-%m-%d %H:%M', applied_at) as applied_at
    FROM beta_users 
    ORDER BY applied_at DESC
    ''')
    
    users = cursor.fetchall()
    
    # Get stats
    cursor.execute('SELECT total_users, approved_users, pending_users FROM beta_stats')
    stats = cursor.fetchone()
    
    conn.close()
    
    # Generate HTML table
    table_rows = ''
    for user in users:
        status_color = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }.get(user[5], 'gray')
        
        table_rows += f'''
        <tr>
            <td>{user[0]}</td>
            <td>{user[1]}</td>
            <td>{user[2]}</td>
            <td>{user[3] or '-'}</td>
            <td>{user[4]}</td>
            <td><span style="color:{status_color}; font-weight:bold;">{user[5].upper()}</span></td>
            <td>{user[6]}</td>
            <td>
                <button onclick="updateStatus({user[0]}, 'approved')" class="btn-approve">✅ Approve</button>
                <button onclick="updateStatus({user[0]}, 'rejected')" class="btn-reject">❌ Reject</button>
            </td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Beta Admin Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ background: #4a6fa5; color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
            .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; flex: 1; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .stat-value {{ font-size: 2.5rem; font-weight: bold; color: #4a6fa5; }}
            .table-container {{ background: white; padding: 20px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; font-weight: bold; }}
            tr:hover {{ background: #f5f5f5; }}
            .btn-approve {{ background: #28a745; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px; }}
            .btn-reject {{ background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }}
            .nav {{ margin-bottom: 20px; }}
            .nav a {{ color: #4a6fa5; text-decoration: none; margin-right: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">← Main Dashboard</a>
                <a href="/beta">← Beta Home</a>
            </div>
            
            <div class="header">
                <h1>🚀 Beta Testing Admin Dashboard</h1>
                <p>Manage beta applications and user access</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{stats[0] if stats else 0}</div>
                    <div>Total Applicants</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats[1] if stats else 0}</div>
                    <div>Approved Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats[2] if stats else 0}</div>
                    <div>Pending Review</div>
                </div>
            </div>
            
            <div class="table-container">
                <h2>All Applications</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Email</th>
                            <th>Name</th>
                            <th>Company</th>
                            <th>Use Case</th>
                            <th>Status</th>
                            <th>Applied At</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            async function updateStatus(userId, status) {{
                if (confirm(`Are you sure you want to ${{status}} this application?`)) {{
                    const response = await fetch('/beta/api/update-status', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ user_id: userId, status: status }})
                    }});
                    
                    const result = await response.json();
                    if (result.success) {{
                        alert('Status updated successfully!');
                        location.reload();
                    }} else {{
                        alert('Error: ' + result.message);
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    '''

@beta_bp.route('/api/apply', methods=['POST'])
def api_apply():
    """API endpoint for beta application"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('name'):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    try:
        conn = sqlite3.connect('beta_users.db')
        cursor = conn.cursor()
        
        # Insert application
        cursor.execute('''
        INSERT INTO beta_users (email, name, company, use_case, details)
        VALUES (?, ?, ?, ?, ?)
        ''', (data['email'], data['name'], data.get('company'), 
              data.get('use_case'), data.get('details', '')))
        
        # Update stats
        cursor.execute('''
        UPDATE beta_stats 
        SET total_users = total_users + 1,
            pending_users = pending_users + 1,
            last_updated = ?
        ''', (datetime.now(),))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Application submitted successfully'
        })
        
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already registered'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@beta_bp.route('/api/stats')
def api_stats():
    """Get beta statistics"""
    conn = sqlite3.connect('beta_users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT total_users, approved_users, pending_users FROM beta_stats')
    stats = cursor.fetchone()
    
    conn.close()
    
    return jsonify({
        'total_users': stats[0] if stats else 0,
        'approved_users': stats[1] if stats else 0,
        'pending_users': stats[2] if stats else 0
    })

@beta_bp.route('/api/update-status', methods=['POST'])
def api_update_status():
    """Update user status (approve/reject)"""
    data = request.get_json()
    
    if not data or not data.get('user_id') or not data.get('status'):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    try:
        conn = sqlite3.connect('beta_users.db')
        cursor = conn.cursor()
        
        # Get current status
        cursor.execute('SELECT status FROM beta_users WHERE id = ?', (data['user_id'],))
        current = cursor.fetchone()
        
        if not current:
            return jsonify({'success': False, 'message': 'User not found'})
        
        current_status = current[0]
        new_status = data['status']
        
        # Update user
        cursor.execute('''
        UPDATE beta_users 
        SET status = ?, approved_at = ?
        WHERE id = ?
        ''', (new_status, datetime.now() if new_status == 'approved' else None, data['user_id']))
        
        # Update stats
        if current_status != new_status:
            if new_status == 'approved':
                cursor.execute('''
                UPDATE beta_stats 
                SET approved_users = approved_users + 1,
                    pending_users = pending_users - 1,
                    last_updated = ?
                ''', (datetime.now(),))
            elif new_status == 'rejected' and current_status == 'pending':
                cursor.execute('''
                UPDATE beta_stats 
                SET pending_users = pending_users - 1,
                    last_updated = ?
                ''', (datetime.now(),))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Status updated'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@beta_bp.route('/api/users')
def api_users():
    """Get all beta users"""
    conn = sqlite3.connect('beta_users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM beta_users ORDER BY applied_at DESC')
    users = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify(users)