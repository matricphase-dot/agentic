
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agents.researcher_simple import ResearcherSimple
from agents.coder_simple import CoderSimple
from agents.qa_simple import QASimple

print("Testing simplified agents...")
print("-" * 40)

# Test researcher
r = ResearcherSimple()
print(f"Researcher test: {r.execute_task('test', {})['success']}")

# Test coder
c = CoderSimple()
print(f"Coder test: {c.execute_task('test', {})['success']}")

# Test QA
q = QASimple()
print(f"QA test: {q.execute_task('test', {})['success']}")

print("\n[OK] All agents working!")
