# check_modules.py
import os

print("🔍 CHECKING EXISTING MODULES...")
print("=" * 50)

# List all Python files
files = [f for f in os.listdir('.') if f.endswith('.py')]
modules = []

# Common module patterns
module_patterns = {
    'teaching': ['teaching_', 'teach_'],
    'agents': ['agent_', 'multi_agent'],
    'desktop': ['desktop_', 'automation'],
    'performance': ['performance_', 'optimization'],
    'distributed': ['distributed_', 'cluster'],
    'failure': ['failure_', 'failure'],
    'vision': ['vision_', 'computer_vision', 'cv_'],
    'nlp': ['nlp_', 'natural_language'],
    'workflow': ['workflow_', 'pipeline'],
    'api': ['api_', 'rest_'],
    'database': ['database_', 'db_'],
    'monitoring': ['monitoring_', 'monitor_']
}

for file in files:
    print(f"📄 {file}")
    
print("\n" + "=" * 50)
print("🎯 MODULES FOUND:")

# Check for specific module files
for file in files:
    file_lower = file.lower()
    
    if 'teaching' in file_lower:
        print(f"✅ Teaching System: {file}")
    elif 'agent' in file_lower and 'module' in file_lower:
        print(f"✅ Agents System: {file}")
    elif 'desktop' in file_lower and 'auto' in file_lower:
        print(f"✅ Desktop Automation: {file}")
    elif 'performance' in file_lower:
        print(f"✅ Performance: {file}")
    elif 'distributed' in file_lower:
        print(f"✅ Distributed: {file}")
    elif 'failure' in file_lower:
        print(f"✅ Failure Analysis (Week 25-26): {file}")
    elif 'vision' in file_lower:
        print(f"✅ Computer Vision (Week 17-18): {file}")
    elif 'nlp' in file_lower:
        print(f"✅ NLP (Week 19-20): {file}")
    elif 'success' in file_lower or 'learning' in file_lower:
        print(f"✅ Success Learning (Week 27-28): {file}")
    elif 'auto_opt' in file_lower:
        print(f"✅ Auto Optimization (Week 29-30): {file}")
    elif 'multi_modal' in file_lower:
        print(f"✅ Multi-Modal (Week 33-40): {file}")

print("\n" + "=" * 50)
print("💡 To fix dashboard, update app.py with ALL found modules")