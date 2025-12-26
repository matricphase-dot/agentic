# diagnostic_imports.py
import sys
import os

print("🔍 Running import diagnostics...")
print(f"Python path: {sys.executable}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path entries: {sys.path[:3]}...")

try:
    print("\n1. Trying to import agents.orchestrator...")
    import agents.orchestrator
    print("✅ Successfully imported agents.orchestrator")
    print(f"   Available names: {[name for name in dir(agents.orchestrator) if not name.startswith('_')]}")
except ImportError as e:
    print(f"❌ Failed: {e}")

try:
    print("\n2. Trying to import from agents.orchestrator directly...")
    from agents.orchestrator import MultiAgentOrchestrator
    print("✅ Successfully imported MultiAgentOrchestrator")
except ImportError as e:
    print(f"❌ Failed: {e}")

try:
    print("\n3. Checking agents package...")
    import agents
    print(f"✅ agents package found at: {agents.__file__}")
    print(f"   agents.__all__: {getattr(agents, '__all__', 'Not defined')}")
    print(f"   agents contents: {[x for x in dir(agents) if not x.startswith('_')]}")
except ImportError as e:
    print(f"❌ Failed: {e}")

print("\n📁 Checking file structure...")
if os.path.exists("agents"):
    print("✅ agents directory exists")
    print("   Contents:", os.listdir("agents"))
    if os.path.exists("agents/__init__.py"):
        print("✅ agents/__init__.py exists")
        with open("agents/__init__.py", "r") as f:
            content = f.read()
            print(f"   First 5 lines:\n{chr(10).join(content.split(chr(10))[:5])}")
    else:
        print("❌ agents/__init__.py missing")