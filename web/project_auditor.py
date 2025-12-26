import os
import sys
import importlib.util
import json
from pathlib import Path

class ProjectAuditor:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.results = {
            "core_agents": {},
            "key_modules": {},
            "infrastructure": {},
            "roadmap_coverage": {}
        }
        
    def check_file_exists(self, path, description):
        """Check if a file exists and report its status."""
        full_path = self.base_path / path
        exists = full_path.exists()
        size = full_path.stat().st_size if exists else 0
        return {
            "exists": exists,
            "size_bytes": size,
            "description": description
        }
    
    def test_module_import(self, module_name, module_path):
        """Safely test if a Python module can be found without executing it."""
        try:
            full_path = self.base_path / module_path
            if not full_path.exists():
                return {"importable": False, "error": "File not found"}
            
            # Just check if we can create a spec - don't execute the module
            spec = importlib.util.spec_from_file_location(module_name, str(full_path))
            if spec is not None and spec.loader is not None:
                return {"importable": True, "error": None}
            else:
                return {"importable": False, "error": "Could not create module spec"}
        except Exception as e:
            return {"importable": False, "error": str(e)}
    
    def analyze_agent_system(self):
        """Analyze the multi-agent system components."""
        agents = ["planner", "researcher", "coder", "qa", "executor", "teacher"]
        for agent in agents:
            # Check for agent-specific files
            agent_file = f"{agent}_agent.py"
            self.results["core_agents"][agent] = self.check_file_exists(agent_file, f"{agent.capitalize()} Agent")
            
            # Check for tests
            test_file = f"test_{agent}_agent.py"
            self.results["core_agents"][agent]["has_tests"] = (self.base_path / test_file).exists()
    
    def analyze_key_modules(self):
        """Check for key system modules mentioned in your roadmap."""
        modules_to_check = [
            ("desktop_automation.py", "Desktop Automation Framework"),
            ("teaching_system.py", "Teaching System"),
            ("success_learning.py", "Success Pattern Learning"),
            ("failure_analysis.py", "Failure Analysis Engine"),
            ("auto_optimization.py", "Automatic Optimization"),
            ("computer_vision.py", "Computer Vision Module"),
            ("workflow_orchestrator.py", "Workflow Orchestrator")
        ]
        
        for file_name, description in modules_to_check:
            self.results["key_modules"][file_name] = self.check_file_exists(file_name, description)
            
            # Try to check if it's a valid Python module (without executing it)
            if file_name.endswith('.py'):
                module_name = file_name[:-3]
                import_result = self.test_module_import(module_name, file_name)
                self.results["key_modules"][file_name].update(import_result)
    
    def analyze_infrastructure(self):
        """Check for infrastructure and configuration files."""
        infra_files = [
            ("requirements.txt", "Python dependencies"),
            ("Dockerfile", "Container configuration"),
            ("docker-compose.yml", "Multi-container setup"),
            (".env.example", "Environment configuration"),
            ("database/", "Database directory"),
            ("tests/", "Test directory"),
            ("docs/", "Documentation")
        ]
        
        for file_name, description in infra_files:
            self.results["infrastructure"][file_name] = self.check_file_exists(file_name, description)
    
    def analyze_roadmap_coverage(self):
        """Map current implementation to your 54-week roadmap."""
        roadmap_phases = {
            "Weeks 1-10": ["Core Multi-Agent System"],
            "Weeks 11-14": ["Teaching System Framework"],
            "Weeks 15-16": ["Desktop Automation"],
            "Weeks 17-24": ["Enhanced Automation (Computer Vision)"],
            "Weeks 25-32": ["Self-Improving System"],
            "Weeks 33-40": ["Multi-Modal Capabilities"],
            "Weeks 41-48": ["Enterprise Features"],
            "Weeks 49-54": ["Market Domination"]
        }
        
        # Simple heuristic: check for key files related to each phase
        phase_indicators = {
            "Core Multi-Agent System": ["planner_agent.py", "multi_agent_system.py"],
            "Teaching System Framework": ["teaching_system.py", "workflow_recorder.py"],
            "Desktop Automation": ["desktop_automation.py", "pyautogui"],
            "Enhanced Automation": ["computer_vision.py", "enhanced_desktop.py"],
            "Self-Improving System": ["success_learning.py", "auto_optimization.py"],
            "Multi-Modal Capabilities": ["multi_modal.py", "vision_processor.py"],
            "Enterprise Features": ["enterprise_dashboard.py", "user_management.py"],
            "Market Domination": ["analytics_dashboard.py", "competitor_tracker.py"]
        }
        
        for phase, features in roadmap_phases.items():
            coverage = []
            for feature in features:
                if feature in phase_indicators:
                    indicators = phase_indicators[feature]
                    # Check if any indicator file exists
                    found = False
                    for indicator in indicators:
                        if indicator.endswith('.py'):
                            # Check for Python file
                            if (self.base_path / indicator).exists():
                                found = True
                                break
                        else:
                            # Check for package/directory
                            if (self.base_path / indicator).exists():
                                found = True
                                break
                            # Check if it's an importable module name
                            try:
                                __import__(indicator)
                                found = True
                                break
                            except ImportError:
                                pass
                    
                    coverage.append({"feature": feature, "implemented": found})
            
            self.results["roadmap_coverage"][phase] = {
                "features": coverage,
                "completion_percentage": sum(1 for c in coverage if c["implemented"]) / len(coverage) * 100 if coverage else 0
            }
    
    def run_audit(self):
        """Execute full audit of the project."""
        print("🔍 Starting Agentic Workflow Engine Audit...")
        print(f"📁 Project Directory: {self.base_path.absolute()}\n")
        
        print("Analyzing agent system...")
        self.analyze_agent_system()
        
        print("Analyzing key modules...")
        self.analyze_key_modules()
        
        print("Analyzing infrastructure...")
        self.analyze_infrastructure()
        
        print("Analyzing roadmap coverage...")
        self.analyze_roadmap_coverage()
        
        print("Generating report...\n")
        return self.generate_report()
    
    def generate_report(self):
        """Generate a comprehensive audit report."""
        report = "\n" + "="*60 + "\n"
        report += "AGENTIC WORKFLOW ENGINE - IMPLEMENTATION AUDIT\n"
        report += "="*60 + "\n\n"
        
        # Summary Statistics
        total_agents = len(self.results["core_agents"])
        implemented_agents = sum(1 for agent in self.results["core_agents"].values() if agent["exists"])
        
        total_modules = len(self.results["key_modules"])
        existing_modules = sum(1 for module in self.results["key_modules"].values() if module["exists"])
        
        report += f"📊 SUMMARY:\n"
        report += f"  • Core Agents: {implemented_agents}/{total_agents} implemented\n"
        report += f"  • Key Modules: {existing_modules}/{total_modules} files exist\n"
        
        # Core Agents Analysis
        report += "\n🤖 CORE AGENT SYSTEM:\n"
        for agent_name, data in self.results["core_agents"].items():
            status = "✅" if data["exists"] else "❌"
            tests = "✓" if data.get("has_tests", False) else "✗"
            report += f"  {status} {agent_name.capitalize()}: {data['description']} [Tests: {tests}]\n"
        
        # Key Modules Analysis
        report += "\n🔧 KEY MODULES:\n"
        for module_name, data in self.results["key_modules"].items():
            status = "✅" if data.get("importable", False) else "⚠️" if data["exists"] else "❌"
            report += f"  {status} {module_name}: {data['description']}"
            if data.get("error") and not data.get("importable", False):
                report += f" - Error: {data['error'][:50]}..."
            report += "\n"
        
        # Infrastructure Analysis
        report += "\n🏗️  INFRASTRUCTURE:\n"
        for item_name, data in self.results["infrastructure"].items():
            status = "✅" if data["exists"] else "❌"
            report += f"  {status} {item_name}: {data['description']}\n"
        
        # Roadmap Analysis
        report += "\n🗺️  ROADMAP COVERAGE:\n"
        for phase, data in self.results["roadmap_coverage"].items():
            percentage = data["completion_percentage"]
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            report += f"  {phase}: {bar} {percentage:.1f}%\n"
        
        # Implementation Gaps
        report += "\n⚠️  CRITICAL GAPS IDENTIFIED:\n"
        gaps = []
        
        # Check for missing revolutionary components
        revolutionary_modules = [
            ("autonomous_designer.py", "Module that autonomously designs workflows"),
            ("process_discovery.py", "System that observes and maps business processes"),
            ("self_healing.py", "System that repairs broken automations"),
            ("marketplace_orchestrator.py", "Decentralized agent coordination")
        ]
        
        for module, description in revolutionary_modules:
            if not (self.base_path / module).exists():
                gaps.append(f"  • {module}: {description}")
        
        if gaps:
            report += "\n".join(gaps)
        else:
            report += "  None - Your system already has revolutionary components!"
        
        # Recommendations based on the partial output we saw earlier
        report += "\n\n🎯 RECOMMENDATIONS BASED ON PARTIAL OUTPUT:\n"
        report += "  From your previous run, we saw these systems INITIALIZED:\n"
        report += "  • ✅ Failure Analysis Engine (Week 25-26) - WITH AUTO-FIX\n"
        report += "  • ✅ Success Pattern Learning - WITH 24 PATTERNS\n"
        report += "  • ✅ Automatic Optimization Engine\n"
        report += "  • ✅ Desktop Automation (PyAutoGUI)\n"
        report += "\n  NEXT STEPS:\n"
        report += "  1. Fix NumPy/OpenCV compatibility (run: pip install 'numpy<2' opencv-python-headless)\n"
        report += "  2. Create a master orchestrator to connect all 6 agents end-to-end\n"
        report += "  3. Test the self-improving loop on a real task\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report

# Main execution
if __name__ == "__main__":
    # Set your project path here
    project_path = "D:/agentic-core/web"  # Update this if different
    
    print("🚀 Agentic Workflow Engine - Implementation Analyzer")
    print("This tool will audit your project structure and implementation status.\n")
    
    # Use current directory if the specified path doesn't exist
    if not os.path.exists(project_path):
        print(f"Note: Path '{project_path}' not found. Using current directory.")
        project_path = "."
    
    auditor = ProjectAuditor(project_path)
    report = auditor.run_audit()
    
    # Save report to file with UTF-8 encoding
    try:
        with open("project_audit_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("📄 Full report saved to 'project_audit_report.txt'")
    except Exception as e:
        print(f"⚠️ Could not save report: {e}")
        print("Here's the report output:\n")
    
    print(report)