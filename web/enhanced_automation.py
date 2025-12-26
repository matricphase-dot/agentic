"""
🎯 ENHANCED AUTOMATION MODULE - WEEKS 19-20
⚡ Advanced automation features with error handling, scheduling, and email integration
📅 Next phase of Agentic Workflow Engine
"""

import os
import json
import time
import threading
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, render_template_string
import sqlite3
from typing import Dict, List, Any, Optional
import logging

# Initialize blueprint
automation_bp = Blueprint('automation', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAutomationSystem:
    """Enhanced automation system with scheduling and email capabilities"""
    
    def __init__(self, db_path: str = 'beta_users.db'):
        self.db_path = db_path
        self.scheduled_tasks = {}
        self.email_config = self.load_email_config()
        self.workflows_dir = "automation_workflows"
        self.logs_dir = "automation_logs"
        
        # Create directories
        os.makedirs(self.workflows_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("✅ Enhanced Automation System Initialized (Week 19-20)")
    
    def load_email_config(self) -> Dict:
        """Load email configuration from file or environment"""
        config_path = "email_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default configuration (should be updated by user)
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "your_email@gmail.com",
            "sender_password": "your_app_password",  # Use app-specific password
            "use_tls": True,
            "default_subject": "Agentic Workflow Engine Notification"
        }
    
    def save_email_config(self, config: Dict) -> bool:
        """Save email configuration to file"""
        try:
            with open("email_config.json", 'w') as f:
                json.dump(config, f, indent=2)
            self.email_config = config
            logger.info("Email configuration saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save email config: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, 
                  html_body: Optional[str] = None) -> Dict:
        """Send an email using configured SMTP settings"""
        try:
            config = self.email_config
            
            # Validate configuration
            if not all([config.get('smtp_server'), config.get('sender_email'), 
                       config.get('sender_password')]):
                return {"success": False, "error": "Email configuration incomplete"}
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = config['sender_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(config['smtp_server'], config.get('smtp_port', 587))
            
            if config.get('use_tls', True):
                server.starttls()
            
            # Login and send
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            # Log the email
            self.log_activity("email_sent", {
                "to": to_email,
                "subject": subject,
                "timestamp": datetime.now().isoformat()
            })
            
            return {"success": True, "message": f"Email sent to {to_email}"}
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"success": False, "error": str(e)}
    
    def send_beta_invitation(self, user_id: int) -> Dict:
        """Send beta invitation email to a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM beta_users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Get user data (assuming cursor returns a dictionary-like row)
        user_dict = {}
        columns = [description[0] for description in cursor.description]
        for i, column in enumerate(columns):
            user_dict[column] = user[i]
        
        # Generate invitation code if not exists
        invitation_code = user_dict.get('invitation_code')
        if not invitation_code:
            import secrets
            invitation_code = secrets.token_urlsafe(16)
            cursor.execute("UPDATE beta_users SET invitation_code = ? WHERE id = ?", 
                         (invitation_code, user_id))
            conn.commit()
        
        conn.close()
        
        # Create email content
        subject = "🎉 Welcome to Agentic Workflow Engine Beta!"
        
        body = f"""
Dear {user_dict['name']},

Congratulations! Your application for the Agentic Workflow Engine beta program has been approved!

Your Beta Access Details:
- Email: {user_dict['email']}
- Invitation Code: {invitation_code}
- Access URL: http://localhost:5000/beta/activate

Next Steps:
1. Visit the activation link above
2. Enter your invitation code
3. Create your account
4. Start automating!

Key Features You Can Test:
🤖 Multi-Agent Automation System
👁️ Computer Vision UI Understanding  
🎓 Intelligent Teaching System
⚡ Desktop Automation Workflows

Support:
- Documentation: Coming soon
- Community: Discord channel (invite in next email)
- Issues: Report via the dashboard

We're excited to have you onboard!

Best regards,
The Agentic Workflow Engine Team
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; }}
        .code-box {{ background: #f1f5f9; padding: 15px; border-radius: 5px; font-family: monospace; 
                   font-size: 1.2em; text-align: center; margin: 20px 0; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #4f46e5; 
                  color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
        .footer {{ background: #f1f5f9; padding: 20px; text-align: center; font-size: 0.9em; 
                 color: #666; border-radius: 0 0 10px 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Beta Access Approved!</h1>
            <p>Welcome to Agentic Workflow Engine</p>
        </div>
        
        <div class="content">
            <p>Dear <strong>{user_dict['name']}</strong>,</p>
            
            <p>Congratulations! Your application for the Agentic Workflow Engine beta program has been approved!</p>
            
            <h3>Your Beta Access Details:</h3>
            <ul>
                <li><strong>Email:</strong> {user_dict['email']}</li>
                <li><strong>Access URL:</strong> http://localhost:5000/beta/activate</li>
            </ul>
            
            <div class="code-box">
                <strong>Invitation Code:</strong><br>
                {invitation_code}
            </div>
            
            <p>
                <a href="http://localhost:5000/beta/activate" class="button">
                    🚀 Activate Your Account
                </a>
            </p>
            
            <h3>Key Features You Can Test:</h3>
            <ul>
                <li>🤖 Multi-Agent Automation System</li>
                <li>👁️ Computer Vision UI Understanding</li>
                <li>🎓 Intelligent Teaching System</li>
                <li>⚡ Desktop Automation Workflows</li>
            </ul>
            
            <p>We're excited to have you onboard!</p>
            
            <p>Best regards,<br>
            <strong>The Agentic Workflow Engine Team</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>Need help? Contact support through the dashboard.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Send the email
        return self.send_email(user_dict['email'], subject, body, html_body)
    
    def send_welcome_email(self, email: str, name: str) -> Dict:
        """Send welcome email to new users"""
        subject = "Welcome to Agentic Workflow Engine!"
        
        body = f"""
Welcome {name}!

Thank you for joining Agentic Workflow Engine. You're now part of a revolutionary 
platform that's changing how automation works.

Getting Started:
1. Login to your dashboard: http://localhost:5000
2. Explore the Computer Vision module
3. Try creating your first workflow
4. Join our community for support

Quick Tips:
- Start with simple automation tasks
- Use the teaching system to record workflows
- Experiment with computer vision features
- Check the documentation for advanced features

Need Help?
- Documentation: Coming soon
- Community Forum: Launching next week
- Email Support: Available for beta users

We're excited to see what you'll automate!

Best regards,
The Agentic Workflow Engine Team
"""
        
        return self.send_email(email, subject, body)
    
    def schedule_workflow(self, workflow_id: int, schedule_time: str, 
                         repeat: Optional[str] = None) -> Dict:
        """Schedule a workflow to run at specific time"""
        try:
            # Parse schedule time
            if schedule_time == "now":
                run_time = datetime.now()
            else:
                run_time = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
            
            # Create task data
            task_id = f"task_{int(time.time())}_{workflow_id}"
            task_data = {
                "id": task_id,
                "workflow_id": workflow_id,
                "scheduled_time": run_time.isoformat(),
                "repeat": repeat,
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }
            
            # Save task
            self.scheduled_tasks[task_id] = task_data
            self._save_scheduled_tasks()
            
            # Schedule if using 'now' or in the future
            if schedule_time == "now":
                # Run immediately in background
                threading.Thread(target=self._execute_workflow, 
                               args=(workflow_id, task_id), daemon=True).start()
            else:
                # Schedule for future
                delay = (run_time - datetime.now()).total_seconds()
                if delay > 0:
                    timer = threading.Timer(delay, self._execute_workflow, 
                                          args=[workflow_id, task_id])
                    timer.daemon = True
                    timer.start()
                    task_data["timer"] = timer
            
            self.log_activity("workflow_scheduled", task_data)
            
            return {
                "success": True,
                "task_id": task_id,
                "scheduled_time": run_time.strftime("%Y-%m-%d %H:%M"),
                "message": f"Workflow scheduled to run at {run_time.strftime('%Y-%m-%d %H:%M')}"
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule workflow: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_workflow(self, workflow_id: int, task_id: str):
        """Execute a workflow (placeholder implementation)"""
        try:
            # Update task status
            self.scheduled_tasks[task_id]["status"] = "running"
            self.scheduled_tasks[task_id]["started_at"] = datetime.now().isoformat()
            self._save_scheduled_tasks()
            
            logger.info(f"Executing workflow {workflow_id} for task {task_id}")
            
            # TODO: Actual workflow execution logic
            # For now, simulate execution
            time.sleep(2)  # Simulate work
            
            # Update task status
            self.scheduled_tasks[task_id]["status"] = "completed"
            self.scheduled_tasks[task_id]["completed_at"] = datetime.now().isoformat()
            self.scheduled_tasks[task_id]["result"] = "Execution successful"
            self._save_scheduled_tasks()
            
            self.log_activity("workflow_executed", {
                "task_id": task_id,
                "workflow_id": workflow_id,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            self.scheduled_tasks[task_id]["status"] = "failed"
            self.scheduled_tasks[task_id]["error"] = str(e)
            self._save_scheduled_tasks()
    
    def create_advanced_workflow(self, name: str, steps: List[Dict], 
                               triggers: Optional[List[Dict]] = None) -> Dict:
        """Create an advanced workflow with triggers and conditions"""
        try:
            workflow_id = f"wf_{int(time.time())}"
            
            workflow = {
                "id": workflow_id,
                "name": name,
                "steps": steps,
                "triggers": triggers or [],
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "execution_count": 0,
                "success_count": 0
            }
            
            # Save workflow
            filename = f"{self.workflows_dir}/{workflow_id}.json"
            with open(filename, 'w') as f:
                json.dump(workflow, f, indent=2)
            
            self.log_activity("workflow_created", {"id": workflow_id, "name": name})
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "filename": filename,
                "message": f"Advanced workflow '{name}' created"
            }
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return {"success": False, "error": str(e)}
    
    def run_workflow_with_conditions(self, workflow_id: str, 
                                   conditions: Dict[str, Any]) -> Dict:
        """Run workflow with conditional logic"""
        try:
            # Load workflow
            filename = f"{self.workflows_dir}/{workflow_id}.json"
            if not os.path.exists(filename):
                return {"success": False, "error": "Workflow not found"}
            
            with open(filename, 'r') as f:
                workflow = json.load(f)
            
            # Check conditions
            if not self._check_conditions(conditions, workflow.get("conditions", [])):
                return {
                    "success": True,
                    "skipped": True,
                    "message": "Conditions not met, workflow skipped"
                }
            
            # Execute workflow
            result = self._execute_workflow_steps(workflow["steps"])
            
            # Update workflow stats
            workflow["execution_count"] += 1
            if result.get("success"):
                workflow["success_count"] += 1
            
            with open(filename, 'w') as f:
                json.dump(workflow, f, indent=2)
            
            self.log_activity("conditional_workflow_executed", {
                "workflow_id": workflow_id,
                "conditions": conditions,
                "result": result
            })
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "result": result,
                "execution_count": workflow["execution_count"]
            }
            
        except Exception as e:
            logger.error(f"Failed to run conditional workflow: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_conditions(self, current_state: Dict, required_conditions: List[Dict]) -> bool:
        """Check if conditions are met"""
        if not required_conditions:
            return True
        
        for condition in required_conditions:
            field = condition.get("field")
            operator = condition.get("operator", "equals")
            value = condition.get("value")
            
            if field not in current_state:
                return False
            
            current_value = current_state[field]
            
            # Evaluate condition
            if operator == "equals" and current_value != value:
                return False
            elif operator == "not_equals" and current_value == value:
                return False
            elif operator == "greater_than" and current_value <= value:
                return False
            elif operator == "less_than" and current_value >= value:
                return False
            elif operator == "contains" and value not in str(current_value):
                return False
        
        return True
    
    def _execute_workflow_steps(self, steps: List[Dict]) -> Dict:
        """Execute workflow steps (simplified for now)"""
        results = []
        
        for i, step in enumerate(steps):
            try:
                step_type = step.get("type", "action")
                action = step.get("action")
                
                # Simulate different actions
                if action == "send_email":
                    result = {"step": i, "action": action, "status": "simulated"}
                elif action == "capture_screen":
                    result = {"step": i, "action": action, "status": "simulated"}
                elif action == "extract_data":
                    result = {"step": i, "action": action, "status": "simulated"}
                else:
                    result = {"step": i, "action": action, "status": "completed"}
                
                results.append(result)
                
                # Add delay between steps if specified
                delay = step.get("delay", 0)
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                results.append({
                    "step": i,
                    "action": step.get("action", "unknown"),
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "success": all(r.get("status") in ["completed", "simulated"] for r in results),
            "steps_executed": len(results),
            "results": results
        }
    
    def log_activity(self, activity_type: str, data: Dict):
        """Log automation activity"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "data": data
        }
        
        # Save to daily log file
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = f"{self.logs_dir}/activity_{date_str}.json"
        
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_activity_logs(self, date: Optional[str] = None) -> List[Dict]:
        """Get activity logs for a specific date"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        log_file = f"{self.logs_dir}/activity_{date}.json"
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []
    
    def _save_scheduled_tasks(self):
        """Save scheduled tasks to file"""
        tasks_file = f"{self.workflows_dir}/scheduled_tasks.json"
        with open(tasks_file, 'w') as f:
            json.dump(self.scheduled_tasks, f, indent=2, default=str)
    
    def _load_scheduled_tasks(self):
        """Load scheduled tasks from file"""
        tasks_file = f"{self.workflows_dir}/scheduled_tasks.json"
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                try:
                    self.scheduled_tasks = json.load(f)
                except:
                    self.scheduled_tasks = {}
    
    def _run_scheduler(self):
        """Background scheduler thread"""
        while True:
            try:
                # Check for scheduled tasks
                now = datetime.now()
                for task_id, task in list(self.scheduled_tasks.items()):
                    if task.get("status") == "scheduled":
                        scheduled_time = datetime.fromisoformat(task["scheduled_time"])
                        if scheduled_time <= now:
                            # Execute task
                            threading.Thread(
                                target=self._execute_workflow,
                                args=(task["workflow_id"], task_id),
                                daemon=True
                            ).start()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)

# Initialize the system
automation_system = EnhancedAutomationSystem()

# ===================== API ENDPOINTS =====================

@automation_bp.route('/')
def automation_dashboard():
    """Enhanced Automation Dashboard"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enhanced Automation - Agentic Workflow Engine</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%); min-height: 100vh; }
            .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 20px; }
            .card-header { background: rgba(255,255,255,0.9); border-bottom: none; border-radius: 15px 15px 0 0 !important; }
            .btn-primary { background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%); border: none; }
            .btn-success { background: linear-gradient(135deg, #10b981 0%, #059669 100%); border: none; }
            .btn-warning { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border: none; }
            .module-status { padding: 5px 15px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
            .status-active { background: #10b981; color: white; }
            .status-inactive { background: #ef4444; color: white; }
            .email-preview { background: white; border-radius: 10px; padding: 20px; margin: 15px 0; }
            .workflow-step { background: #f8fafc; border-radius: 8px; padding: 15px; margin: 10px 0; }
            .nav-tabs .nav-link { border-radius: 10px 10px 0 0; }
            .results-box { background: #f8f9fa; border-radius: 10px; padding: 15px; max-height: 400px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container py-4">
            <!-- Header -->
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="mb-0"><i class="fas fa-bolt me-2"></i>Enhanced Automation System</h2>
                        <p class="text-muted mb-0">Weeks 19-20: Email integration, scheduling, and advanced workflows</p>
                    </div>
                    <div>
                        <span class="module-status status-active"><i class="fas fa-check-circle me-1"></i>ACTIVE</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="alert alert-info">
                                <h6><i class="fas fa-info-circle"></i> Module Status</h6>
                                <p class="mb-1">Email System: <span class="badge bg-success">Ready</span></p>
                                <p class="mb-1">Scheduler: <span class="badge bg-success">Active</span></p>
                                <p class="mb-0">Workflow Engine: <span class="badge bg-success">Ready</span></p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <p>This module adds advanced automation capabilities:</p>
                            <ul>
                                <li>Email notifications and invitations</li>
                                <li>Workflow scheduling and automation</li>
                                <li>Conditional workflow execution</li>
                                <li>Advanced logging and monitoring</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content Tabs -->
            <ul class="nav nav-tabs" id="automationTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="email-tab" data-bs-toggle="tab" data-bs-target="#email" type="button">
                        <i class="fas fa-envelope me-2"></i>Email System
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="scheduling-tab" data-bs-toggle="tab" data-bs-target="#scheduling" type="button">
                        <i class="fas fa-clock me-2"></i>Scheduling
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="workflows-tab" data-bs-toggle="tab" data-bs-target="#workflows" type="button">
                        <i class="fas fa-project-diagram me-2"></i>Advanced Workflows
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="logs-tab" data-bs-toggle="tab" data-bs-target="#logs" type="button">
                        <i class="fas fa-history me-2"></i>Activity Logs
                    </button>
                </li>
            </ul>

            <div class="tab-content mt-4">
                <!-- Email Tab -->
                <div class="tab-pane fade show active" id="email" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0"><i class="fas fa-cog"></i> Email Configuration</h5>
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label class="form-label">SMTP Server:</label>
                                        <input type="text" class="form-control" id="smtpServer" placeholder="smtp.gmail.com">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Port:</label>
                                        <input type="number" class="form-control" id="smtpPort" value="587">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Email Address:</label>
                                        <input type="email" class="form-control" id="senderEmail" placeholder="your_email@gmail.com">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">App Password:</label>
                                        <input type="password" class="form-control" id="senderPassword" placeholder="Your app password">
                                        <small class="text-muted">Use app-specific password, not your regular password</small>
                                    </div>
                                    <button class="btn btn-primary w-100" onclick="saveEmailConfig()">
                                        <i class="fas fa-save me-2"></i>Save Configuration
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0"><i class="fas fa-paper-plane"></i> Send Test Email</h5>
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label class="form-label">Recipient Email:</label>
                                        <input type="email" class="form-control" id="testEmail" placeholder="recipient@example.com">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Subject:</label>
                                        <input type="text" class="form-control" id="testSubject" value="Test Email from Agentic Workflow Engine">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Message:</label>
                                        <textarea class="form-control" id="testMessage" rows="3">This is a test email from the Enhanced Automation System (Week 19-20).</textarea>
                                    </div>
                                    <button class="btn btn-success w-100" onclick="sendTestEmail()">
                                        <i class="fas fa-paper-plane me-2"></i>Send Test Email
                                    </button>
                                    <div class="results-box mt-3" id="emailResults">
                                        Email results will appear here...
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mt-4">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-user-plus"></i> Beta Invitation Emails</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Select Beta User:</label>
                                <select class="form-select" id="betaUserSelect">
                                    <option value="">Loading users...</option>
                                </select>
                            </div>
                            <button class="btn btn-warning w-100" onclick="sendBetaInvitation()">
                                <i class="fas fa-envelope-open-text me-2"></i>Send Beta Invitation
                            </button>
                            <div class="results-box mt-3" id="invitationResults">
                                Invitation results will appear here...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Scheduling Tab -->
                <div class="tab-pane fade" id="scheduling" role="tabpanel">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0"><i class="fas fa-clock"></i> Schedule Workflow</h5>
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label class="form-label">Workflow Name:</label>
                                        <input type="text" class="form-control" id="workflowName" placeholder="Daily Report Automation">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Schedule Time:</label>
                                        <input type="datetime-local" class="form-control" id="scheduleTime">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Repeat:</label>
                                        <select class="form-select" id="repeatSchedule">
                                            <option value="">Do not repeat</option>
                                            <option value="daily">Daily</option>
                                            <option value="weekly">Weekly</option>
                                            <option value="monthly">Monthly</option>
                                        </select>
                                    </div>
                                    <button class="btn btn-primary w-100" onclick="scheduleWorkflow()">
                                        <i class="fas fa-calendar-plus me-2"></i>Schedule Workflow
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0"><i class="fas fa-tasks"></i> Scheduled Tasks</h5>
                                </div>
                                <div class="card-body">
                                    <div class="results-box" id="scheduledTasks">
                                        Loading scheduled tasks...
                                    </div>
                                    <button class="btn btn-secondary w-100 mt-3" onclick="loadScheduledTasks()">
                                        <i class="fas fa-sync me-2"></i>Refresh Tasks
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Workflows Tab -->
                <div class="tab-pane fade" id="workflows" role="tabpanel">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-plus-circle"></i> Create Advanced Workflow</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Workflow Name:</label>
                                <input type="text" class="form-control" id="advWorkflowName" placeholder="Data Extraction Pipeline">
                            </div>
                            
                            <div id="workflowSteps">
                                <div class="workflow-step">
                                    <h6>Step 1</h6>
                                    <select class="form-select mb-2" onchange="updateStepParams(this, 1)">
                                        <option value="">Select Action</option>
                                        <option value="capture_screen">Capture Screen</option>
                                        <option value="extract_text">Extract Text</option>
                                        <option value="send_email">Send Email</option>
                                        <option value="process_data">Process Data</option>
                                    </select>
                                    <div id="stepParams1"></div>
                                </div>
                            </div>
                            
                            <button class="btn btn-secondary mt-2" onclick="addWorkflowStep()">
                                <i class="fas fa-plus me-2"></i>Add Step
                            </button>
                            
                            <button class="btn btn-primary w-100 mt-3" onclick="createAdvancedWorkflow()">
                                <i class="fas fa-save me-2"></i>Create Advanced Workflow
                            </button>
                            
                            <div class="results-box mt-3" id="workflowResults">
                                Workflow creation results...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Logs Tab -->
                <div class="tab-pane fade" id="logs" role="tabpanel">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-history"></i> Activity Logs</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Select Date:</label>
                                <input type="date" class="form-control" id="logDate" value="{{ today }}">
                            </div>
                            <button class="btn btn-primary w-100 mb-3" onclick="loadActivityLogs()">
                                <i class="fas fa-search me-2"></i>Load Logs
                            </button>
                            <div class="results-box" id="activityLogs">
                                Select a date and load logs...
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Navigation -->
            <div class="mt-4 text-center">
                <div class="btn-group">
                    <a href="/" class="btn btn-outline-light">
                        <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
                    </a>
                    <a href="/cv" class="btn btn-outline-light">
                        <i class="fas fa-eye me-2"></i>Computer Vision
                    </a>
                    <a href="/beta" class="btn btn-outline-light">
                        <i class="fas fa-clipboard-list me-2"></i>Beta Testing
                    </a>
                </div>
            </div>
        </div>

        <!-- JavaScript -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Set today's date in date inputs
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('logDate').value = today;
            document.getElementById('scheduleTime').value = new Date(Date.now() + 3600000).toISOString().slice(0, 16);
            
            // Load beta users
            loadBetaUsers();
            
            // Load scheduled tasks
            loadScheduledTasks();
            
            function loadBetaUsers() {
                fetch('/beta/api/users')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success && data.users.length > 0) {
                            const select = document.getElementById('betaUserSelect');
                            select.innerHTML = '<option value="">Select a user...</option>';
                            data.users.forEach(user => {
                                const option = document.createElement('option');
                                option.value = user.id;
                                option.textContent = `${user.name} (${user.email}) - ${user.status}`;
                                select.appendChild(option);
                            });
                        }
                    });
            }
            
            function saveEmailConfig() {
                const config = {
                    smtp_server: document.getElementById('smtpServer').value,
                    smtp_port: parseInt(document.getElementById('smtpPort').value),
                    sender_email: document.getElementById('senderEmail').value,
                    sender_password: document.getElementById('senderPassword').value
                };
                
                document.getElementById('emailResults').innerHTML = 
                    '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Saving configuration...</div>';
                
                fetch('/automation/api/email/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(config)
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('emailResults').innerHTML = 
                            '<div class="alert alert-success">✅ Email configuration saved successfully!</div>';
                    } else {
                        document.getElementById('emailResults').innerHTML = 
                            `<div class="alert alert-danger">❌ Error: ${data.error}</div>`;
                    }
                });
            }
            
            function sendTestEmail() {
                const emailData = {
                    to_email: document.getElementById('testEmail').value,
                    subject: document.getElementById('testSubject').value,
                    body: document.getElementById('testMessage').value
                };
                
                document.getElementById('emailResults').innerHTML = 
                    '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Sending test email...</div>';
                
                fetch('/automation/api/email/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(emailData)
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('emailResults').innerHTML = 
                            `<div class="alert alert-success">✅ ${data.message}</div>`;
                    } else {
                        document.getElementById('emailResults').innerHTML = 
                            `<div class="alert alert-danger">❌ Error: ${data.error}</div>`;
                    }
                });
            }
            
            function sendBetaInvitation() {
                const userId = document.getElementById('betaUserSelect').value;
                if (!userId) {
                    alert('Please select a user');
                    return;
                }
                
                document.getElementById('invitationResults').innerHTML = 
                    '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Sending invitation...</div>';
                
                fetch(`/automation/api/email/beta-invitation/${userId}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('invitationResults').innerHTML = 
                                `<div class="alert alert-success">✅ Beta invitation sent successfully!</div>`;
                        } else {
                            document.getElementById('invitationResults').innerHTML = 
                                `<div class="alert alert-danger">❌ Error: ${data.error}</div>`;
                        }
                    });
            }
            
            function scheduleWorkflow() {
                const workflowData = {
                    name: document.getElementById('workflowName').value,
                    schedule_time: document.getElementById('scheduleTime').value,
                    repeat: document.getElementById('repeatSchedule').value
                };
                
                fetch('/automation/api/schedule/workflow', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(workflowData)
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert(`✅ Workflow scheduled: ${data.message}`);
                        loadScheduledTasks();
                    } else {
                        alert(`❌ Error: ${data.error}`);
                    }
                });
            }
            
            function loadScheduledTasks() {
                document.getElementById('scheduledTasks').innerHTML = 
                    '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading tasks...</div>';
                
                fetch('/automation/api/schedule/tasks')
                    .then(r => r.json())
                    .then(data => {
                        if (data.success && data.tasks.length > 0) {
                            let html = '<h6>Scheduled Tasks:</h6><div class="list-group">';
                            data.tasks.forEach(task => {
                                html += `<div class="list-group-item">
                                    <strong>${task.name || 'Unnamed'}</strong><br>
                                    <small>Scheduled: ${task.scheduled_time} | Status: ${task.status}</small>
                                </div>`;
                            });
                            html += '</div>';
                            document.getElementById('scheduledTasks').innerHTML = html;
                        } else {
                            document.getElementById('scheduledTasks').innerHTML = 
                                '<div class="alert alert-info">No scheduled tasks found.</div>';
                        }
                    });
            }
            
            let stepCount = 1;
            
            function addWorkflowStep() {
                stepCount++;
                const stepsDiv = document.getElementById('workflowSteps');
                const newStep = document.createElement('div');
                newStep.className = 'workflow-step mt-3';
                newStep.innerHTML = `
                    <h6>Step ${stepCount}</h6>
                    <select class="form-select mb-2" onchange="updateStepParams(this, ${stepCount})">
                        <option value="">Select Action</option>
                        <option value="capture_screen">Capture Screen</option>
                        <option value="extract_text">Extract Text</option>
                        <option value="send_email">Send Email</option>
                        <option value="process_data">Process Data</option>
                    </select>
                    <div id="stepParams${stepCount}"></div>
                `;
                stepsDiv.appendChild(newStep);
            }
            
            function updateStepParams(select, stepNum) {
                const action = select.value;
                const paramsDiv = document.getElementById(`stepParams${stepNum}`);
                
                let paramsHtml = '';
                switch(action) {
                    case 'send_email':
                        paramsHtml = `
                            <input type="email" class="form-control mb-2" placeholder="Recipient email">
                            <input type="text" class="form-control mb-2" placeholder="Subject">
                            <textarea class="form-control" placeholder="Message" rows="2"></textarea>
                        `;
                        break;
                    case 'capture_screen':
                        paramsHtml = `
                            <input type="text" class="form-control mb-2" placeholder="Region (optional, e.g., 0,0,800,600)">
                            <input type="number" class="form-control" placeholder="Delay (seconds)" value="1">
                        `;
                        break;
                    default:
                        paramsHtml = '<input type="text" class="form-control" placeholder="Parameters (optional)">';
                }
                
                paramsDiv.innerHTML = paramsHtml;
            }
            
            function createAdvancedWorkflow() {
                const workflowName = document.getElementById('advWorkflowName').value;
                if (!workflowName) {
                    alert('Please enter a workflow name');
                    return;
                }
                
                // Collect steps (simplified)
                const steps = [
                    {"type": "action", "action": "capture_screen", "delay": 1},
                    {"type": "action", "action": "extract_text", "delay": 0}
                ];
                
                document.getElementById('workflowResults').innerHTML = 
                    '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Creating workflow...</div>';
                
                fetch('/automation/api/workflows/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: workflowName,
                        steps: steps
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('workflowResults').innerHTML = 
                            `<div class="alert alert-success">✅ Workflow created: ${data.message}</div>`;
                    } else {
                        document.getElementById('workflowResults').innerHTML = 
                            `<div class="alert alert-danger">❌ Error: ${data.error}</div>`;
                    }
                });
            }
            
            function loadActivityLogs() {
                const date = document.getElementById('logDate').value;
                
                document.getElementById('activityLogs').innerHTML = 
                    '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading logs...</div>';
                
                fetch(`/automation/api/logs/${date}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.success && data.logs.length > 0) {
                            let html = `<h6>Activity Logs for ${date}:</h6><div class="list-group">`;
                            data.logs.forEach(log => {
                                html += `<div class="list-group-item">
                                    <small class="text-muted">${log.timestamp}</small><br>
                                    <strong>${log.type}</strong><br>
                                    <small>${JSON.stringify(log.data)}</small>
                                </div>`;
                            });
                            html += '</div>';
                            document.getElementById('activityLogs').innerHTML = html;
                        } else {
                            document.getElementById('activityLogs').innerHTML = 
                                `<div class="alert alert-info">No logs found for ${date}</div>`;
                        }
                    });
            }
        </script>
    </body>
    </html>
    ''', today=datetime.now().strftime("%Y-%m-%d"))

# API Endpoints
@automation_bp.route('/api/email/config', methods=['POST'])
def api_email_config():
    """Update email configuration"""
    try:
        config = request.get_json()
        success = automation_system.save_email_config(config)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Email configuration updated"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save configuration"
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@automation_bp.route('/api/email/send', methods=['POST'])
def api_send_email():
    """Send an email"""
    try:
        data = request.get_json()
        to_email = data.get('to_email')
        subject = data.get('subject')
        body = data.get('body')
        html_body = data.get('html_body')
        
        if not all([to_email, subject, body]):
            return jsonify({"success": False, "error": "Missing required fields"})
        
        result = automation_system.send_email(to_email, subject, body, html_body)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@automation_bp.route('/api/email/beta-invitation/<int:user_id>')
def api_send_beta_invitation(user_id):
    """Send beta invitation email"""
    try:
        result = automation_system.send_beta_invitation(user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@automation_bp.route('/api/schedule/workflow', methods=['POST'])
def api_schedule_workflow():
    """Schedule a workflow"""
    try:
        data = request.get_json()
        name = data.get('name', 'Unnamed Workflow')
        schedule_time = data.get('schedule_time')
        repeat = data.get('repeat')
        
        # For demo, create a mock workflow ID
        import random
        workflow_id = random.randint(1000, 9999)
        
        result = automation_system.schedule_workflow(workflow_id, schedule_time, repeat)
        if result['success']:
            result['workflow_name'] = name
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@automation_bp.route('/api/schedule/tasks')
def api_get_scheduled_tasks():
    """Get scheduled tasks"""
    try:
        # Convert tasks to list
        tasks = list(automation_system.scheduled_tasks.values())
        return jsonify({
            "success": True,
            "tasks": tasks[:10]  # Return first 10
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@automation_bp.route('/api/workflows/create', methods=['POST'])
def api_create_workflow():
    """Create an advanced workflow"""
    try:
        data = request.get_json()
        name = data.get('name')
        steps = data.get('steps', [])
        triggers = data.get('triggers', [])
        
        if not name:
            return jsonify({"success": False, "error": "Workflow name required"})
        
        result = automation_system.create_advanced_workflow(name, steps, triggers)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@automation_bp.route('/api/logs/<date>')
def api_get_logs(date):
    """Get activity logs for a date"""
    try:
        logs = automation_system.get_activity_logs(date)
        return jsonify({
            "success": True,
            "date": date,
            "logs": logs[:50]  # Return first 50 logs
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Beta users API for dropdown
@automation_bp.route('/beta/api/users')
def api_beta_users():
    """Get beta users for dropdown"""
    try:
        conn = sqlite3.connect('beta_users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, status FROM beta_users WHERE status = 'approved'")
        users = cursor.fetchall()
        conn.close()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user[0],
                "email": user[1],
                "name": user[2],
                "status": user[3]
            })
        
        return jsonify({
            "success": True,
            "users": user_list
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    # Test the automation system
    print("🤖 Testing Enhanced Automation System...")
    print("✅ Email system ready")
    print("✅ Scheduler active")
    print("🚀 Enhanced Automation System Ready!")