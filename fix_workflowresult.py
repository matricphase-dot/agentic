# fix_workflowresult.py
with open("agents/orchestrator.py", "r") as f:
    lines = f.readlines()

# Find and replace the WorkflowResult class
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    
    # Look for the WorkflowResult class definition
    if "class WorkflowResult" in line and i > 0 and "@dataclass" in lines[i-1]:
        # Skip to the end of the class
        while i < len(lines) and not lines[i].startswith("class ") and "@dataclass" not in lines[i]:
            i += 1
            if i < len(lines):
                line = lines[i]
                if line.startswith("class ") or "@dataclass" in line:
                    break
                new_lines.append(line)
        
        # Insert the corrected class
        new_lines.pop()  # Remove the last added line
        new_lines.append('@dataclass')
        new_lines.append('class WorkflowResult:')
        new_lines.append('    """Result of a workflow execution with deep observability"""')
        new_lines.append('    success: bool')
        new_lines.append('    output: Any')
        new_lines.append('    error: Optional[str] = None')
        new_lines.append('    steps: List[StepExecution] = field(default_factory=list)')
        new_lines.append('    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))')
        new_lines.append('    start_time: datetime = field(default_factory=datetime.now)')
        new_lines.append('    end_time: Optional[datetime] = None')
        new_lines.append('    ')
        new_lines.append('    @property')
        new_lines.append('    def total_duration(self) -> Optional[float]:')
        new_lines.append('        """Calculate total duration as a property"""')
        new_lines.append('        if self.end_time and self.start_time:')
        new_lines.append('            return (self.end_time - self.start_time).total_seconds()')
        new_lines.append('        return None')
        new_lines.append('    ')
        new_lines.append('    performance_metrics: Dict = field(default_factory=dict)')
        new_lines.append('')
        continue
    
    i += 1

with open("agents/orchestrator_fixed.py", "w") as f:
    f.writelines(new_lines)

print("✅ Created agents/orchestrator_fixed.py")
print("Now rename: del agents\\orchestrator.py && rename agents\\orchestrator_fixed.py orchestrator.py")