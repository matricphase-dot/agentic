# File: D:\agentic-core\start.py
"""
Quick start script for Agentic Workflow Engine - Phase 2.5 Complete!
"""

import sys
import os

def main():
    print("="*80)
    print("AGENTIC WORKFLOW ENGINE - PHASE 2.5 COMPLETE")
    print("="*80)
    
    print("\nAvailable commands:")
    print("1. Test the system: python test_phase_25.py")
    print("2. Run a workflow: python -c \"from agents.orchestrator_ascii import OrchestratorASCII; o=OrchestratorASCII(); o.execute_workflow('Check langchain version')\"")
    print("3. View reports: dir workflow_report_*.json")
    print("4. Start interactive: python interactive.py")
    
    print("\nExample workflows to try:")
    print("  - 'Check langchain version'")
    print("  - 'Get weather in London'")
    print("  - 'Create a calculator function'")
    print("  - 'Scrape website data'")
    
    print("\n" + "="*80)
    print("🎉 PHASE 2.5: MICROSCOPIC PoC COMPLETE!")
    print("Next: Phase 2 - Robust Core (Month 2-4)")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())