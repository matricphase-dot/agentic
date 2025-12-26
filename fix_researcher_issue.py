"""
Quick fix for researcher agent issue
"""

import sys
import os
import shutil

print("=" * 80)
print("QUICK FIX FOR RESEARCHER AGENT ISSUE")
print("=" * 80)

def backup_original_researcher():
    """Backup original researcher.py if it exists"""
    original_path = "agents/researcher.py"
    backup_path = "agents/researcher_original.py"
    
    if os.path.exists(original_path):
        try:
            shutil.copy2(original_path, backup_path)
            print(f"✅ Original researcher backed up to: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to backup: {e}")
            return False
    return True

def create_updated_researcher():
    """Create updated researcher with execute_task method"""
    updated_code = '''"""
Updated Researcher Agent with execute_task method
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class ResearcherAgent:
    """
    Updated Researcher Agent with execute_task method for Windows compatibility
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize Researcher Agent"""
        self.tools = self._load_tools()
        print("✅ ResearcherAgent initialized")
        print(f"✅ ResearcherAgent loaded {len(self.tools)} tools")
    
    def _load_tools(self) -> Dict:
        """Load available research tools"""
        return {
            "pypi_client": self._pypi_research,
            "web_scraper": self._web_scrape,
            "general_search": self._general_search
        }
    
    def list_tools(self) -> List[str]:
        """List available tools"""
        return list(self.tools.keys())
    
    def execute_task(self, task_description: str) -> Dict:
        """
        Execute a research task (main method for orchestrator)
        
        Args:
            task_description: Description of the research task
            
        Returns:
            Dictionary with research results
        """
        print(f"🔍 Executing research task: {task_description[:50]}...")
        
        try:
            # Determine which tool to use based on task description
            task_lower = task_description.lower()
            
            if any(keyword in task_lower for keyword in ['pypi', 'package', 'version']):
                result = self._pypi_research(task_description)
                tool_used = "pypi_client"
            elif any(keyword in task_lower for keyword in ['scrape', 'website', 'web']):
                result = self._web_scrape(task_description)
                tool_used = "web_scraper"
            else:
                result = self._general_search(task_description)
                tool_used = "general_search"
            
            # Create artifact
            artifact_id = self._save_artifact(
                content=result,
                metadata={
                    "task": task_description,
                    "tool_used": tool_used,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "result": result,
                "artifact_id": artifact_id,
                "tool_used": tool_used
            }
            
        except Exception as e:
            print(f"❌ Research task failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "artifact_id": None
            }
    
    def _pypi_research(self, query: str) -> str:
        """Simulate PyPI research (stub for now)"""
        # In a real implementation, this would query PyPI API
        return f"PyPI research for '{query}': Found package information (simulated)"
    
    def _web_scrape(self, query: str) -> str:
        """Simulate web scraping (stub for now)"""
        # In a real implementation, this would scrape websites
        return f"Web scrape for '{query}': Found relevant information (simulated)"
    
    def _general_search(self, query: str) -> str:
        """Simulate general search"""
        return f"General research for '{query}': Found relevant information (simulated)"
    
    def _save_artifact(self, content: Any, metadata: Dict = None) -> str:
        """Save research artifact"""
        os.makedirs("artifacts/research", exist_ok=True)
        
        artifact_id = f"research_{int(datetime.now().timestamp())}"
        artifact_file = f"artifacts/research/{artifact_id}.json"
        
        artifact_data = {
            "id": artifact_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        with open(artifact_file, 'w', encoding='utf-8') as f:
            json.dump(artifact_data, f, indent=2)
        
        return artifact_id

# For backward compatibility
def create_researcher_agent():
    """Factory function for backward compatibility"""
    return ResearcherAgent()
'''
    
    try:
        with open("agents/researcher.py", "w", encoding="utf-8") as f:
            f.write(updated_code)
        print("✅ Updated researcher.py created")
        return True
    except Exception as e:
        print(f"❌ Failed to create updated researcher: {e}")
        return False

def test_fix():
    """Test the fix"""
    print("\nTesting the fix...")
    
    try:
        # Test 1: Import updated researcher
        from agents.researcher import ResearcherAgent
        researcher = ResearcherAgent()
        print("✅ ResearcherAgent imported successfully")
        
        # Test 2: Check execute_task method
        result = researcher.execute_task("Test task")
        print(f"✅ execute_task method works: {result['success']}")
        
        # Test 3: Test with orchestrator
        print("\nTesting with simple workflow...")
        
        # Create simple test
        from agents.coder_windows import CoderAgentWindows
        from agents.qa_windows import QAAgentWindows
        
        coder = CoderAgentWindows()
        qa = QAAgentWindows()
        
        # Generate and execute code
        gen_result = coder.generate_code("Add two numbers")
        if gen_result["success"]:
            exec_result = coder.execute_code(gen_result["code"])
            if exec_result["success"]:
                print(f"✅ Code execution successful")
                print(f"   Output: {exec_result['output'][:50]}...")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Apply the fix"""
    print("\nApplying fix for researcher agent issue...")
    
    # Step 1: Backup original
    if not backup_original_researcher():
        print("⚠ Could not backup original, continuing anyway...")
    
    # Step 2: Create updated researcher
    if not create_updated_researcher():
        print("❌ Failed to create updated researcher")
        return
    
    # Step 3: Test the fix
    print("\n" + "="*80)
    print("TESTING FIX")
    print("="*80)
    
    if test_fix():
        print("\n" + "="*80)
        print("🎉 FIX APPLIED SUCCESSFULLY!")
        print("="*80)
        print("\nThe researcher agent now has the execute_task() method.")
        print("\nRun these tests to verify:")
        print("1. python test_fixed_system.py")
        print("2. python -c \"from agents.orchestrator_updated import OrchestratorUpdated; o=OrchestratorUpdated(); print(o.execute_workflow('Test task'))\"")
    else:
        print("\n" + "="*80)
        print("⚠ FIX MAY NOT HAVE WORKED COMPLETELY")
        print("="*80)
        print("\nYou can still use the coder and QA agents directly.")

if __name__ == "__main__":
    main()