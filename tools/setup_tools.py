# File: D:\agentic-core\tools\setup_tools.py (Minimal)
print("="*80)
print("MINIMAL TOOL SETUP FOR PHASE 2")
print("="*80)

from tools.registry import ToolRegistry

# Create registry
registry = ToolRegistry()

# Create simple tools
class PyPITool:
    def execute(self, params):
        return {"success": True, "result": f"Checked package: {params.get('package', 'unknown')}"}

# Register tools
from tools.registry import ToolMetadata, ToolCapability

pypi_metadata = ToolMetadata(
    tool_id="pypi_001",
    name="PyPI Client",
    version="1.0",
    author="System",
    capabilities=[
        ToolCapability(
            name="check_version",
            description="Check Python package version",
            input_schema={},
            output_schema={},
            keywords=["python", "package", "version"]
        )
    ]
)

registry.register_tool(PyPITool(), pypi_metadata)

print(f"\nRegistered {len(registry.tools)} tools")
print("Phase 2 tool system ready!")