# monitoring/telemetry_system.py
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EventType(Enum):
    TASK_START = "task_start"
    AGENT_DECISION = "agent_decision"
    TOOL_CALL = "tool_call"
    LLM_CALL = "llm_call"
    STEP_COMPLETE = "step_complete"
    TASK_COMPLETE = "task_complete"
    ERROR = "error"
    GUARDRAIL_TRIGGERED = "guardrail_triggered"

@dataclass
class TelemetryEvent:
    """Immutable record of a single event in the agent's execution[citation:1]"""
    event_id: str
    trace_id: str  # Connects all events for a single user task[citation:1]
    parent_event_id: Optional[str]
    event_type: EventType
    component: str  # e.g., "planner", "researcher", "orchestrator"
    timestamp: str
    data: Dict[str, Any]  # Structured event details

    def to_dict(self):
        return asdict(self)

class TelemetrySystem:
    """
    Production-ready telemetry system for agentic workflows.
    Persists everything for replay, debugging, and learning[citation:1].
    """
    
    def __init__(self, storage_path: str = "monitoring/traces"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._active_traces = {}
        
    def start_trace(self, task: str, workflow_id: Optional[str] = None) -> str:
        """Start a new distributed trace for a user task[citation:1]"""
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        self._active_traces[trace_id] = {
            "task": task,
            "workflow_id": workflow_id,
            "start_time": datetime.now().isoformat(),
            "events": [],
            "root_event": None
        }
        
        # Create root event
        root_event = TelemetryEvent(
            event_id=f"root_{trace_id}",
            trace_id=trace_id,
            parent_event_id=None,
            event_type=EventType.TASK_START,
            component="orchestrator",
            timestamp=datetime.now().isoformat(),
            data={"task": task, "workflow_id": workflow_id}
        )
        
        self._record_event(trace_id, root_event)
        logger.info(f"📊 Trace started: {trace_id} for task: {task}")
        return trace_id
    
    def record_agent_decision(self, trace_id: str, agent: str, 
                            input: Dict, decision: Dict, reasoning: Optional[str] = None):
        """Record an agent's reasoning and decision"""
        event = TelemetryEvent(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            parent_event_id=self._get_last_event_id(trace_id),
            event_type=EventType.AGENT_DECISION,
            component=agent,
            timestamp=datetime.now().isoformat(),
            data={
                "agent": agent,
                "input": input,
                "decision": decision,
                "reasoning": reasoning,
                "model_used": decision.get("model", "default")
            }
        )
        self._record_event(trace_id, event)
    
    def record_tool_call(self, trace_id: str, tool_name: str, 
                        parameters: Dict, result: Dict, duration_ms: float):
        """Record a tool execution with timing and result"""
        event = TelemetryEvent(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            parent_event_id=self._get_last_event_id(trace_id),
            event_type=EventType.TOOL_CALL,
            component=tool_name,
            timestamp=datetime.now().isoformat(),
            data={
                "tool": tool_name,
                "parameters": parameters,
                "result": result,
                "duration_ms": duration_ms,
                "success": result.get("success", False)
            }
        )
        self._record_event(trace_id, event)
    
    def record_llm_call(self, trace_id: str, model: str, prompt: str,
                       completion: str, tokens_used: Dict, cost_estimate: float):
        """Record LLM call for cost tracking and prompt engineering[citation:4]"""
        # Sanitize large prompts for storage
        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt
        
        event = TelemetryEvent(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            parent_event_id=self._get_last_event_id(trace_id),
            event_type=EventType.LLM_CALL,
            component="llm",
            timestamp=datetime.now().isoformat(),
            data={
                "model": model,
                "prompt_preview": prompt_preview,
                "completion_preview": completion[:500],
                "tokens_used": tokens_used,
                "cost_estimate": cost_estimate,
                "prompt_hash": hash(prompt)  # For deduplication analysis
            }
        )
        self._record_event(trace_id, event)
    
    def end_trace(self, trace_id: str, success: bool, 
                 final_output: Any, error: Optional[str] = None):
        """Complete a trace and persist to durable storage[citation:1]"""
        if trace_id not in self._active_traces:
            return False
        
        trace_data = self._active_traces[trace_id]
        trace_data["end_time"] = datetime.now().isoformat()
        trace_data["success"] = success
        trace_data["final_output"] = str(final_output)[:1000]  # Truncate if large
        trace_data["error"] = error
        
        # Calculate duration
        start = datetime.fromisoformat(trace_data["start_time"])
        end = datetime.fromisoformat(trace_data["end_time"])
        trace_data["duration_seconds"] = (end - start).total_seconds()
        
        # Persist the complete trace
        filename = f"{trace_id}.json"
        filepath = self.storage_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(trace_data, f, indent=2, default=str)
        
        logger.info(f"📁 Trace persisted: {filename} "
                   f"({len(trace_data['events'])} events, "
                   f"{trace_data['duration_seconds']:.2f}s)")
        
        # Remove from active traces
        del self._active_traces[trace_id]
        return True
    
    def _record_event(self, trace_id: str, event: TelemetryEvent):
        """Internal method to record an event"""
        if trace_id in self._active_traces:
            self._active_traces[trace_id]["events"].append(event.to_dict())
    
    def _get_last_event_id(self, trace_id: str) -> Optional[str]:
        """Get the ID of the most recent event in a trace"""
        if (trace_id in self._active_traces and 
            self._active_traces[trace_id]["events"]):
            return self._active_traces[trace_id]["events"][-1]["event_id"]
        return None
    
    def get_trace(self, trace_id: str) -> Optional[Dict]:
        """Load a completed trace from storage"""
        filepath = self.storage_path / f"{trace_id}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def analyze_trace(self, trace_id: str) -> Dict:
        """Analyze a trace for performance and cost insights[citation:4]"""
        trace = self.get_trace(trace_id)
        if not trace:
            return {"error": "Trace not found"}
        
        analysis = {
            "trace_id": trace_id,
            "task": trace.get("task"),
            "success": trace.get("success", False),
            "duration_seconds": trace.get("duration_seconds", 0),
            "total_events": len(trace.get("events", [])),
            "agent_decisions": 0,
            "tool_calls": 0,
            "llm_calls": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0,
            "error_events": 0,
            "event_breakdown": {}
        }
        
        for event in trace.get("events", []):
            event_type = event.get("event_type")
            analysis["event_breakdown"][event_type] = \
                analysis["event_breakdown"].get(event_type, 0) + 1
            
            if event_type == EventType.AGENT_DECISION.value:
                analysis["agent_decisions"] += 1
            elif event_type == EventType.TOOL_CALL.value:
                analysis["tool_calls"] += 1
            elif event_type == EventType.LLM_CALL.value:
                analysis["llm_calls"] += 1
                # Sum token counts
                tokens = event.get("data", {}).get("tokens_used", {})
                analysis["total_tokens"] += tokens.get("total", 0)
                analysis["estimated_cost"] += event.get("data", {}).get("cost_estimate", 0)
            elif event_type == EventType.ERROR.value:
                analysis["error_events"] += 1
        
        return analysis

# Global instance for easy import
telemetry = TelemetrySystem()