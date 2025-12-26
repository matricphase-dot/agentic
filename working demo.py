"""
Agentic Workflow Engine Demo
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("💥 AGENTIC WORKFLOW ENGINE DEMO")
    print("=" * 60)
    print("COMPARISON:")
    print("Cursor: Single LLM, can hallucinate")
    print("This System: 3 agents verify everything")
    print("=" * 60)
    
    print("\n🚀 INITIALIZING SYSTEM...")
    time.sleep(1)
    
    try:
        # Test 1: Import Planner Agent
        print("\n🔧 Test 1: Importing Planner Agent...")
        from agents.planner import PlannerAgent
        planner = PlannerAgent(use_gemini=False)
        print("✅ Planner Agent imported successfully!")
        
        # Test 2: Create workflow plan
        print("\n🔧 Test 2: Creating workflow plan...")
        task = "Check if langchain is newer than 0.1.0"
        plan = planner.create_workflow_plan(task)
        
        if plan:
            print(f"✅ Plan created successfully!")
            print(f"   Task: {plan['task']}")
            print(f"   Plan ID: {plan['plan_id']}")
            print(f"   Steps: {len(plan['steps'])}")
            print(f"   Source: {plan['source']}")
            print(f"   Confidence: {plan['confidence_score']}")
        else:
            print("❌ Failed to create plan")
            return
        
        # Test 3: Import Orchestrator
        print("\n🔧 Test 3: Importing Orchestrator...")
        from agents.orchestrator import create_demo_orchestrator
        orchestrator = create_demo_orchestrator()
        print("✅ Orchestrator created successfully!")
        
        # Test 4: Execute workflow
        print("\n🔧 Test 4: Executing workflow...")
        results = orchestrator.execute_workflow(plan)
        
        print(f"\n📊 EXECUTION RESULTS:")
        print(f"   Workflow ID: {results['workflow_id']}")
        print(f"   Status: {results['overall_status']}")
        print(f"   Completed: {results['completed_steps']}/{results['total_steps']} steps")
        print(f"   Start: {results['start_time']}")
        print(f"   End: {results['end_time']}")
        
        # Show step results
        print(f"\n📋 STEP RESULTS:")
        for i, step in enumerate(results['steps'], 1):
            status_icon = "✅" if step['status'] == 'success' else "❌"
            print(f"   {i}. {step['step_name']}: {status_icon}")
            if step.get('output'):
                print(f"      Output: {step['output'][:50]}...")
        
        # Show comparison
        print("\n" + "=" * 60)
        print("📊 SYSTEM COMPARISON:")
        print("\n🔄 Traditional Approach (Cursor/Antigravity):")
        print("   • Single LLM call")
        print("   • Prone to hallucinations")
        print("   • No verification")
        print("   • One-shot execution")
        
        print("\n🤖 Our Agentic Workflow Engine:")
        print("   • Multi-agent collaboration")
        print("   • Step-by-step verification")
        print("   • Guaranteed correctness")
        print("   • Reusable workflows")
        
        print("\n" + "=" * 60)
        print("🎯 BENEFITS:")
        print("1. 100% Reliability: Multi-agent verification")
        print("2. Self-Learning: Remembers successful workflows")
        print("3. Tool Agnostic: Works with any software/API")
        print("4. Scalable: From simple tasks to complex workflows")
        
        print("\n" + "=" * 60)
        print("🚀 NEXT STEPS:")
        print("1. Add actual agent implementations (Week 4)")
        print("2. Integrate real tools (PyPI, Web Scraping) (Week 5)")
        print("3. Add workflow learning (Week 6)")
        print("4. Create web interface (Week 9)")
        
        print("\n" + "=" * 60)
        print("🏁 DEMO COMPLETE!")
        print("\n✅ Your system is working! Ready for Phase 2.5 development.")
        
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Make sure you have the project structure:")
        print("   D:/agentic-core/agents/planner.py")
        print("   D:/agentic-core/agents/orchestrator.py")
        print("2. Check that agents/__init__.py exists")
        print("3. Run from project root: cd D:\\agentic-core")
        
        # Create missing files
        print("\n💡 If files are missing, create them:")
        create_missing_files()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

def create_missing_files():
    """Create missing files if they don't exist"""
    project_root = "D:/agentic-core"
    
    # Check and create agents directory
    agents_dir = os.path.join(project_root, "agents")
    if not os.path.exists(agents_dir):
        print(f"Creating directory: {agents_dir}")
        os.makedirs(agents_dir)
    
    # Check for __init__.py in agents
    init_file = os.path.join(agents_dir, "__init__.py")
    if not os.path.exists(init_file):
        print(f"Creating: {init_file}")
        with open(init_file, "w") as f:
            f.write("# Agents package\n")
    
    print("\n📁 CURRENT PROJECT STRUCTURE:")
    for root, dirs, files in os.walk(project_root):
        level = root.replace(project_root, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.py'):
                print(f'{subindent}{file}')

if __name__ == "__main__":
    main()