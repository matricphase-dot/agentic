#!/usr/bin/env python3
"""
Discovery Script for Agentic Workflow Engine
Maps existing functions, classes, and agent logic across modules.
Run this from D:\agentic-core\web to analyze the codebase.
"""

import os
import inspect
import importlib.util
import sys
from pathlib import Path

BASE_DIR = Path("D:/agentic-core/web")
MODULES = [
    "desktop_automation",
    "failure_analysis", 
    "auto_optimization",
    "computer_vision",
    "teaching_system"
]

def discover_module_functions(module_path):
    """Inspect a module and return callable functions/classes."""
    try:
        spec = importlib.util.spec_from_file_location("module", module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["module"] = module
        spec.loader.exec_module(module)
        
        functions = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.isclass(obj):
                try:
                    sig = inspect.signature(obj) if inspect.isfunction(obj) else None
                    functions.append({
                        "name": name,
                        "type": "function" if inspect.isfunction(obj) else "class",
                        "signature": str(sig) if sig else None
                    })
                except:
                    pass
        return functions
    except Exception as e:
        return [{"error": str(e)}]

def find_agent_functions():
    """Search for embedded agent logic (plan, code, analyze, etc.)."""
    agent_keywords = ["plan", "code", "qa", "test", "execute", "analyze", "optimize", "teach"]
    matches = {}
    
    for mod_name in MODULES:
        mod_path = BASE_DIR / f"{mod_name}.py"
        if mod_path.exists():
            funcs = discover_module_functions(str(mod_path))
            agent_matches = [f for f in funcs if any(kw in f.get("name", "").lower() for kw in agent_keywords)]
            if agent_matches:
                matches[mod_name] = agent_matches
    
    return matches

def main():
    print("\n" + "="*70)
    print("🧠 AGENTIC WORKFLOW ENGINE - CODEBASE DISCOVERY")
    print("="*70)
    
    print("\n1️⃣ MODULE STATUS:")
    for mod_name in MODULES:
        mod_path = BASE_DIR / f"{mod_name}.py"
        status = "✅ EXISTS" if mod_path.exists() else "❌ MISSING"
        print(f"   {mod_name}.py: {status}")
    
    print("\n2️⃣ EMBEDDED AGENT FUNCTIONS:")
    agent_funcs = find_agent_functions()
    if agent_funcs:
        for mod, funcs in agent_funcs.items():
            print(f"\n   📦 {mod}:")
            for f in funcs:
                sig = f.get("signature", "")
                print(f"      └─ {f['name']} ({f['type']})")
                if sig and sig != "()":
                    print(f"         {sig}")
    else:
        print("   ⚠️  No agent functions found - check module imports")
    
    print("\n3️⃣ RECOMMENDED ADAPTER MAPPING:")
    print("   • Planner Agent  → Look for: plan(), generate_plan(), create_plan()")
    print("   • Coder Agent    → Look for: code(), generate_script(), generate_code()")
    print("   • Analyzer Agent → Look for: analyze(), analyze_recording(), analyze_session()")
    print("   • QA Agent       → Look for: test(), validate(), check_quality()")
    print("   • Executor Agent → Look for: execute(), run(), deploy()")
    print("   • Teacher Agent  → Look for: teach(), learn(), record_pattern()")
    
    print("\n4️⃣ NEXT STEPS:")
    print("   1. Run: python orchestrator.py")
    print("   2. Follow the prompts to execute a mission")
    print("   3. Check 'deployed_workflow.py' for generated automation")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
