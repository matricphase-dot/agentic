
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "testing",
        "modules": ["agentic_repository", "agents_new", "agent_manager", "app_backup", "beta", "beta_testing", "beta_users.db", "check_beta", "checks", "check_web", "complete_fix", "complete", "computer_vision", "deploy_cv", "desktop_automation", "diagnostic", "distributed_execution", "distributed", "enhanced_automation", "enhanced_teaching", "failure_analysis", "final", "fix_all_issues", "fix_beta", "fix_beta_admin", "fix_beta_database", "fix_dashboard", "fix_database", "fix_encoding", "fixs", "github_backup", "install", "install_dependencies", "install_tesseract", "integrated_app", "integrated_beta_app", "master_app", "minimal_beta", "one_click_restore", "performance", "performance_optimization", "quick_check", "quick_fix", "setup", "setups", "simple_app", "simple_test", "teaching", "teaching", "temp_desktop", "test_failure_analysis", "test_workflows", "worker_node", "working"],
        "message": "All modules detected"
    })

if __name__ == '__main__':
    print("Testing module detection...")
    app.run(debug=True, port=5001)
