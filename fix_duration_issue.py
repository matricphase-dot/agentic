# fix_duration_issue.py
import os

print("🔧 Fixing total_duration issue...")

orchestrator_file = "agents/orchestrator.py"

if os.path.exists(orchestrator_file):
    with open(orchestrator_file, "r") as f:
        content = f.read()
    
    # Find and replace the WorkflowResult class
    if "@dataclass" in content and "class WorkflowResult" in content:
        # Extract the old WorkflowResult class
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        # Copy everything until we find WorkflowResult class
        while i < len(lines):
            new_lines.append(lines[i])
            
            # Check if this line starts the WorkflowResult class
            if "class WorkflowResult" in lines[i] and "@dataclass" in lines[i-1]:
                # Skip old class definition and add the new one
                # Skip until we find the next class definition or end of class
                while i < len(lines) and not lines[i].startswith("class "):
                    i += 1
                
                # Add corrected WorkflowResult class
                new_lines.append("@dataclass")
                new_lines.append("class WorkflowResult:")
                new_lines.append('    """Result of a workflow execution with deep observability"""')
                new_lines.append("    success: bool")
                new_lines.append("    output: Any")
                new_lines.append("    error: Optional[str] = None")
                new_lines.append("    steps: List[StepExecution] = field(default_factory=list)")
                new_lines.append('    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))')
                new_lines.append("    start_time: datetime = field(default_factory=datetime.now)")
                new_lines.append("    end_time: Optional[datetime] = None")
                new_lines.append("    ")
                new_lines.append("    # Changed: Make total_duration a computed property, not a field")
                new_lines.append("    @property")
                new_lines.append("    def total_duration(self) -> Optional[float]:")
                new_lines.append("        if self.end_time and self.start_time:")
                new_lines.append("            return (self.end_time - self.start_time).total_seconds()")
                new_lines.append("        return None")
                new_lines.append("    ")
                new_lines.append("    performance_metrics: Dict = field(default_factory=dict)")
                new_lines.append("    ")
                new_lines.append("    # Removed the __post_init__ method since we're using a property now")
                
                # Skip the old class lines we already passed
                continue
            
            i += 1
        
        # Write back
        with open(orchestrator_file, "w") as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Fixed WorkflowResult class")
    else:
        print("❌ Could not find WorkflowResult class")
    
    # Also fix the execute_workflow method to ensure end_time is set
    with open(orchestrator_file, "r") as f:
        content = f.read()
    
    # Add end_time setting in success case
    if "result.success = True" in content and "result.end_time = datetime.now()" not in content:
        # Find where to insert end_time setting
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            # Insert end_time setting after success = True
            if "result.success = True" in line:
                new_lines.append("            result.end_time = datetime.now()  # This line was missing!")
        
        with open(orchestrator_file, "w") as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Added end_time setting in success case")
    else:
        print("✅ end_time already set in success case")
        
else:
    print(f"❌ {orchestrator_file} not found")

print("\n🎯 Fix applied! Now run the test again.")