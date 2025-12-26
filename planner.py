# agents/planner.py
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Import memory system for similar workflow lookup (Phase 2 feature)
try:
    from memory.artifact_store import ArtifactStore
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("Note: Memory system not available. Planning from scratch.")

# Define structured output models
class WorkflowStep(BaseModel):
    step_id: str = Field(description="Unique identifier for this step")
    agent_type: str = Field(description="Type of agent: researcher, coder, qa, executor, analyzer")
    action: str = Field(description="Specific action with expected inputs/outputs")
    tools_needed: List[str] = Field(default_factory=list, description="Tools required: pypi_client, web_scraper, etc.")
    dependencies: List[str] = Field(default_factory=list, description="Step IDs that must complete first")
    validation_criteria: str = Field(default="", description="How to verify this step succeeded")

class WorkflowPlan(BaseModel):
    """A complete structured workflow plan."""
    task: str = Field(description="Original user task")
    task_id: str = Field(description="Unique identifier for this task instance")
    steps: List[WorkflowStep] = Field(description="Ordered steps to complete task")
    expected_output: str = Field(description="Description of final expected result")
    complexity: str = Field(description="Simple, Medium, Complex")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class PlannerAgent:
    def __init__(self, use_gemini: bool = True):
        """
        Enhanced Planner Agent with Gemini 1.5 Pro and memory lookup.
        """
        self.llm = None
        self.use_gemini = use_gemini
        self.logger = logging.getLogger(__name__)
        
        # Initialize memory if available
        self.memory = None
        if MEMORY_AVAILABLE:
            try:
                self.memory = ArtifactStore()
                self.logger.info("Connected to artifact memory")
            except Exception as e:
                self.logger.warning(f"Could not connect to memory: {e}")
        
        # Initialize Gemini LLM if enabled and API key available
        if use_gemini and os.getenv("GOOGLE_API_KEY"):
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro",
                    temperature=0.1,
                    timeout=30,
                    max_retries=2
                )
                self.logger.info("Gemini 1.5 Pro LLM initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini: {e}")
                self.llm = None
        else:
            if use_gemini:
                self.logger.warning("GOOGLE_API_KEY not found. Using rule-based planner.")
            self.llm = None
    
    def create_workflow_plan(self, task: str, task_id: Optional[str] = None) -> WorkflowPlan:
        """
        Main planning method with memory lookup and intelligent decomposition.
        """
        if not task_id:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Planning workflow for task: '{task}' (ID: {task_id})")
        
        # STEP 1: Check memory for similar workflows
        similar_plan = self._check_memory_for_similar(task)
        if similar_plan:
            self.logger.info(f"Found similar workflow in memory. Adapting...")
            adapted_plan = self._adapt_existing_plan(similar_plan, task, task_id)
            if self._validate_plan(adapted_plan):
                return adapted_plan
        
        # STEP 2: Use LLM to create new plan
        if self.llm:
            try:
                new_plan = self._plan_with_gemini(task, task_id)
                if self._validate_plan(new_plan):
                    # Store successful plan in memory
                    self._store_plan_in_memory(new_plan)
                    return new_plan
            except Exception as e:
                self.logger.error(f"Gemini planning failed: {e}")
        
        # STEP 3: Fallback to rule-based planning
        self.logger.info("Using enhanced rule-based planner")
        return self._enhanced_rule_based_plan(task, task_id)
    
    def _check_memory_for_similar(self, task: str) -> Optional[WorkflowPlan]:
        """Search memory for similar previously successful workflows."""
        if not self.memory:
            return None
        
        try:
            # Simple keyword matching - Phase 4 will use vector similarity
            keywords = self._extract_keywords(task)
            # This would query your Neo4j/ChromaDB in Phase 4
            # For now, return None to force new planning
            return None
        except Exception as e:
            self.logger.debug(f"Memory search error: {e}")
            return None
    
    def _plan_with_gemini(self, task: str, task_id: str) -> WorkflowPlan:
        """Use Gemini 1.5 Pro for intelligent workflow decomposition."""
        
        system_prompt = """You are an expert workflow planner for an AI multi-agent system.
        
        CRITICAL RULES:
        1. Output MUST be valid JSON matching the exact schema
        2. Break complex tasks into 3-7 executable steps
        3. Each step must use exactly one agent type
        4. Specify tools needed for each step
        5. Include clear validation criteria
        
        AGENT CAPABILITIES:
        - researcher: Fetch data from web/APIs/databases
        - coder: Write, execute, debug code
        - qa: Verify correctness, test, validate
        - executor: Run commands, save results
        - analyzer: Process data, generate insights
        
        TOOL REGISTRY: pypi_client, web_scraper, sql_executor, file_handler
        
        EXAMPLE FOR "Check trending Python packages":
        {
            "task": "Check trending Python packages",
            "steps": [
                {
                    "step_id": "fetch_data",
                    "agent_type": "researcher",
                    "action": "Fetch trending packages from PyPI API",
                    "tools_needed": ["web_scraper"],
                    "dependencies": [],
                    "validation_criteria": "Received list of at least 5 packages"
                },
                {
                    "step_id": "get_details",
                    "agent_type": "researcher",
                    "action": "Get version and download stats for each package",
                    "tools_needed": ["pypi_client"],
                    "dependencies": ["fetch_data"],
                    "validation_criteria": "Has version info for all packages"
                }
            ]
        }
        """
        
        human_prompt = f"""Create a workflow plan for this task: {task}
        
        Additional context:
        - Task ID: {task_id}
        - Available tools: pypi_client, web_scraper, compare_versions
        - System can execute Python code safely
        - Final output should be stored as artifact
        
        Return ONLY the JSON object with this exact structure:
        {{
            "task": "task description",
            "task_id": "id_string",
            "steps": [
                {{
                    "step_id": "unique_id",
                    "agent_type": "agent_type",
                    "action": "clear action",
                    "tools_needed": ["tool1"],
                    "dependencies": ["step_id"],
                    "validation_criteria": "how to verify"
                }}
            ],
            "expected_output": "description",
            "complexity": "Simple/Medium/Complex"
        }}
        """
        
        try:
            # Create the prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_prompt)
            ])
            
            # Use JSON output parser for reliable structured output
            parser = JsonOutputParser(pydantic_object=WorkflowPlan)
            chain = prompt | self.llm | parser
            
            # Generate the plan
            result = chain.invoke({"task": task})
            
            # Ensure task_id is set
            result["task_id"] = task_id
            
            return WorkflowPlan(**result)
            
        except Exception as e:
            self.logger.error(f"Error in Gemini planning: {str(e)[:200]}")
            raise
    
    def _enhanced_rule_based_plan(self, task: str, task_id: str) -> WorkflowPlan:
        """Enhanced rule-based planner with better task recognition."""
        task_lower = task.lower()
        
        # Pattern 1: Package version checking
        if any(word in task_lower for word in ["version", "newer than", "compare"]) and \
           any(word in task_lower for word in ["package", "pypi", "library"]):
            
            # Extract package names (simple regex)
            import re
            packages = re.findall(r'(\w+)\s+(?:package|library|on pypi)', task_lower)
            
            steps = []
            if packages:
                for i, pkg in enumerate(packages[:2]):  # Handle up to 2 packages
                    steps.append(WorkflowStep(
                        step_id=f"fetch_{pkg}",
                        agent_type="researcher",
                        action=f"Fetch version information for {pkg} from PyPI",
                        tools_needed=["pypi_client"],
                        dependencies=[],
                        validation_criteria=f"Got version number for {pkg}"
                    ))
                
                if len(packages) > 1:
                    steps.append(WorkflowStep(
                        step_id="compare",
                        agent_type="coder",
                        action=f"Compare versions of {packages[0]} and {packages[1]}",
                        tools_needed=["compare_versions"],
                        dependencies=[f"fetch_{pkg}" for pkg in packages[:2]],
                        validation_criteria="Comparison result is True/False"
                    ))
            
            return WorkflowPlan(
                task=task,
                task_id=task_id,
                steps=steps or [WorkflowStep(
                    step_id="research",
                    agent_type="researcher",
                    action="Research package versions",
                    tools_needed=["pypi_client"],
                    dependencies=[],
                    validation_criteria="Found version information"
                )],
                expected_output="Package version comparison result",
                complexity="Simple"
            )
        
        # Pattern 2: Trending/analysis tasks
        elif any(word in task_lower for word in ["trending", "popular", "top", "analyze"]):
            return WorkflowPlan(
                task=task,
                task_id=task_id,
                steps=[
                    WorkflowStep(
                        step_id="fetch_trending",
                        agent_type="researcher",
                        action="Fetch trending packages from PyPI or GitHub",
                        tools_needed=["web_scraper"],
                        dependencies=[],
                        validation_criteria="Retrieved list of trending packages"
                    ),
                    WorkflowStep(
                        step_id="get_details",
                        agent_type="researcher",
                        action="Get detailed info for each package",
                        tools_needed=["pypi_client"],
                        dependencies=["fetch_trending"],
                        validation_criteria="Has metadata for all packages"
                    ),
                    WorkflowStep(
                        step_id="analyze",
                        agent_type="analyzer",
                        action="Analyze trends and create summary",
                        tools_needed=[],
                        dependencies=["get_details"],
                        validation_criteria="Analysis includes insights"
                    ),
                    WorkflowStep(
                        step_id="format",
                        agent_type="coder",
                        action="Format results for output",
                        tools_needed=[],
                        dependencies=["analyze"],
                        validation_criteria="Output is well-structured"
                    )
                ],
                expected_output="Analysis report of trending packages",
                complexity="Medium"
            )
        
        # Default pattern for unknown tasks
        return WorkflowPlan(
            task=task,
            task_id=task_id,
            steps=[
                WorkflowStep(
                    step_id="research",
                    agent_type="researcher",
                    action=f"Research information about: {task}",
                    tools_needed=["web_scraper"],
                    dependencies=[],
                    validation_criteria="Gathered relevant information"
                ),
                WorkflowStep(
                    step_id="process",
                    agent_type="analyzer",
                    action="Process and analyze the research findings",
                    tools_needed=[],
                    dependencies=["research"],
                    validation_criteria="Analysis completed"
                ),
                WorkflowStep(
                    step_id="verify",
                    agent_type="qa",
                    action="Verify the quality and correctness",
                    tools_needed=[],
                    dependencies=["process"],
                    validation_criteria="Quality checks passed"
                )
            ],
            expected_output="Verified result of the task",
            complexity="Medium"
        )
    
    def _validate_plan(self, plan: WorkflowPlan) -> bool:
        """Comprehensive plan validation."""
        if not plan.steps:
            self.logger.error("Validation failed: No steps in plan")
            return False
        
        # Check for circular dependencies
        step_ids = [step.step_id for step in plan.steps]
        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    self.logger.error(f"Validation failed: Step {step.step_id} depends on unknown step {dep}")
                    return False
        
        # Check for valid agent types
        valid_agents = {"researcher", "coder", "qa", "executor", "analyzer"}
        for step in plan.steps:
            if step.agent_type not in valid_agents:
                self.logger.error(f"Validation failed: Invalid agent type {step.agent_type}")
                return False
        
        self.logger.info(f"Plan validation passed with {len(plan.steps)} steps")
        return True
    
    def _store_plan_in_memory(self, plan: WorkflowPlan):
        """Store successful plan for future reuse."""
        if not self.memory:
            return
        
        try:
            # This would store in Neo4j/ChromaDB in Phase 4
            # For now, just log it
            self.logger.info(f"Plan {plan.task_id} would be stored in memory")
        except Exception as e:
            self.logger.debug(f"Failed to store plan: {e}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Simple keyword extraction for memory lookup."""
        import re
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        # Remove common stopwords
        stopwords = {"the", "and", "for", "with", "from", "this", "that", "what"}
        return [w for w in words if w not in stopwords][:10]
    
    def display_plan(self, plan: WorkflowPlan, detailed: bool = False):
        """Display the workflow plan in readable format."""
        print(f"\n{'='*60}")
        print(f"📋 WORKFLOW PLAN: {plan.task}")
        print(f"ID: {plan.task_id} | Complexity: {plan.complexity}")
        print(f"Created: {plan.created_at}")
        print(f"{'='*60}")
        
        for i, step in enumerate(plan.steps, 1):
            deps = f" ← [{', '.join(step.dependencies)}]" if step.dependencies else ""
            tools = f" 🛠️ {', '.join(step.tools_needed)}" if step.tools_needed else ""
            print(f"\n{i}. [{step.agent_type.upper()}] {step.step_id}{deps}{tools}")
            print(f"   Action: {step.action}")
            if step.validation_criteria and detailed:
                print(f"   ✓ Verify: {step.validation_criteria}")
        
        print(f"\n🎯 Expected Output: {plan.expected_output}")
        print(f"📊 Steps: {len(plan.steps)} | Agents: {len(set(s.agent_type for s in plan.steps))}")
        print(f"{'='*60}")


# Quick test function
def test_planner():
    """Test the enhanced planner."""
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Enhanced Planner Agent...")
    print("-" * 40)
    
    # Test with Gemini if API key available
    has_api_key = os.getenv("GOOGLE_API_KEY")
    planner = PlannerAgent(use_gemini=has_api_key)
    
    test_tasks = [
        "Check if langchain is newer than 0.1.0",
        "What are the top 5 trending Python packages this week?",
        "Compare numpy, pandas, and scikit-learn versions",
        "Analyze PyPI download trends for machine learning libraries"
    ]
    
    for task in test_tasks:
        print(f"\n🔍 Task: {task}")
        try:
            plan = planner.create_workflow_plan(task)
            planner.display_plan(plan, detailed=True)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_planner()