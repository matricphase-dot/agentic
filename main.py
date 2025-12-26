# main.py - Windows compatible version
#!/usr/bin/env python
"""
Main CLI entry point for Agentic Workflow Engine - Windows compatible
"""

import sys
import os
import argparse

# Handle Windows encoding
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

def run_workflow(task: str, use_gemini: bool = True, visualize: bool = True):
    """Run a complete workflow for a given task"""
    print(f"Starting workflow for: {task}")
    print("-" * 60)
    
    try:
        # Initialize planner
        from agents.planner import PlannerAgent
        planner = PlannerAgent(use_gemini=use_gemini)
        
        # Create plan
        plan = planner.create_workflow_plan(task)
        
        # Validate plan
        is_valid, errors = planner.validate_plan(plan)
        
        if not is_valid:
            print("Plan validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        # Visualize if requested
        if visualize:
            print(planner.visualize_plan(plan))
        
        print(f"Plan created successfully!")
        print(f"Steps: {len(plan.steps)} | Estimated: {plan.estimated_duration}s")
        print(f"Tools needed: {', '.join(plan.required_tools)}")
        
        # Execute using orchestrator if available
        try:
            from agents.orchestrator_v5_3 import ToolEnhancedOrchestrator
            orchestrator = ToolEnhancedOrchestrator(use_gemini=use_gemini)
            result = orchestrator.execute_workflow(task)
            
            print(f"\\nWorkflow executed!")
            print(f"  Status: {result.overall_status}")
            print(f"  Duration: {result.total_duration or 0:.2f}s")
            print(f"  Completed steps: {len([s for s in result.steps if s.status.name == 'COMPLETED'])}")
            
            return True
        except ImportError:
            print("\\nOrchestrator not available, plan is ready but not executed")
            return True
            
    except Exception as e:
        print(f"Workflow failed: {e}")
        return False

def interactive_mode():
    """Run in interactive mode"""
    print("Agentic Workflow Engine - Interactive Mode")
    print("=" * 60)
    print("Type 'quit' or 'exit' to leave")
    print("-" * 60)
    
    from agents.planner import PlannerAgent
    planner = PlannerAgent(use_gemini=True)
    
    while True:
        try:
            task = input("\\nEnter task: ").strip()
            
            if task.lower() in ['quit', 'exit', 'q']:
                print("\\nGoodbye!")
                break
            
            if not task:
                continue
            
            print(f"\\nPlanning: {task}")
            plan = planner.create_workflow_plan(task)
            
            is_valid, errors = planner.validate_plan(plan)
            
            if is_valid:
                print(planner.visualize_plan(plan))
                print("Ready to execute!")
            else:
                print("Plan invalid:")
                for error in errors:
                    print(f"  - {error}")
                    
        except KeyboardInterrupt:
            print("\\n\\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agentic Workflow Engine")
    parser.add_argument("task", nargs="?", help="Task to execute")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--no-gemini", action="store_true", help="Disable Gemini API")
    parser.add_argument("--simple", action="store_true", help="Simple output")
    
    args = parser.parse_args()
    
    print("Agentic Workflow Engine v0.1.0")
    print("=" * 60)
    
    if args.interactive:
        interactive_mode()
    elif args.task:
        success = run_workflow(
            task=args.task,
            use_gemini=not args.no_gemini,
            visualize=not args.simple
        )
        sys.exit(0 if success else 1)
    else:
        print("Usage:")
        print("  python main.py 'your task here'")
        print("  python main.py --interactive")
        print("\\nExamples:")
        print("  python main.py 'Check langchain version'")
        print("  python main.py 'Get weather in Tokyo' --no-gemini")
        sys.exit(1)

if __name__ == "__main__":
    main()