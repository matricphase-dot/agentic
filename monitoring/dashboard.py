# monitoring/dashboard.py (COMPLETE FIXED VERSION)
import json
from pathlib import Path
from datetime import datetime, timedelta
import statistics
from typing import List, Dict

def generate_telemetry_report(days_back: int = 1):
    """
    Generate a summary report from telemetry data.
    
    Args:
        days_back: Number of days to look back for traces
    """
    traces_dir = Path("monitoring/traces")
    
    if not traces_dir.exists():
        print("❌ No telemetry data found. Run some tasks first!")
        return
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(days=days_back)
    
    # Collect recent traces
    recent_traces = []
    for trace_file in traces_dir.glob("*.json"):
        try:
            with open(trace_file, 'r') as f:
                trace = json.load(f)
            
            # Check if trace is recent enough
            trace_time = datetime.fromisoformat(trace.get('start_time', '2024-01-01'))
            if trace_time >= cutoff_time:
                recent_traces.append(trace)
        except Exception as e:
            print(f"⚠️  Could not read {trace_file}: {e}")
    
    if not recent_traces:
        print(f"📭 No traces found from the last {days_back} day(s)")
        return
    
    print(f"\n{'='*60}")
    print(f"📊 TELEMETRY DASHBOARD - Last {days_back} day(s)")
    print(f"{'='*60}")
    print(f"Total traces analyzed: {len(recent_traces)}")
    
    # Calculate metrics
    success_rate = sum(1 for t in recent_traces if t.get('success')) / len(recent_traces)
    durations = [t.get('duration_seconds', 0) for t in recent_traces]
    avg_duration = statistics.mean(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    
    # Event counts
    total_events = sum(len(t.get('events', [])) for t in recent_traces)
    events_per_trace = total_events / len(recent_traces) if recent_traces else 0
    
    print(f"\n📈 PERFORMANCE METRICS:")
    print(f"  • Success rate: {success_rate:.1%}")
    print(f"  • Avg. duration: {avg_duration:.2f}s")
    print(f"  • Max duration: {max_duration:.2f}s")
    print(f"  • Avg. events per trace: {events_per_trace:.1f}")
    
    # Tool usage breakdown
    tool_counts = {}
    llm_calls = 0
    agent_decisions = 0
    
    for trace in recent_traces:
        for event in trace.get('events', []):
            if event.get('event_type') == 'tool_call':
                tool = event.get('data', {}).get('tool', 'unknown')
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
            elif event.get('event_type') == 'llm_call':
                llm_calls += 1
            elif event.get('event_type') == 'agent_decision':
                agent_decisions += 1
    
    print(f"\n🛠️  TOOL USAGE (total calls):")
    for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {tool}: {count}")
    
    print(f"\n🧠 AGENT ACTIVITY:")
    print(f"  • LLM Calls: {llm_calls}")
    print(f"  • Agent Decisions: {agent_decisions}")
    
    # Recent traces list
    print(f"\n🕒 RECENT TRACES (newest first):")
    recent_traces.sort(key=lambda x: x.get('start_time', ''), reverse=True)
    
    for i, trace in enumerate(recent_traces[:5]):
        trace_id = trace.get('trace_id', 'unknown')
        task = trace.get('task', 'unknown')[:50]
        success = "✅" if trace.get('success') else "❌"
        duration = trace.get('duration_seconds', 0)
        
        print(f"  {i+1}. {trace_id}")
        print(f"     Task: {task}")
        print(f"     Status: {success} | Duration: {duration:.2f}s | Events: {len(trace.get('events', []))}")
    
    print(f"\n💡 TIP: View detailed trace with:")
    if recent_traces:
        tip_trace_id = recent_traces[0].get("trace_id")
        print(f'     python -c "from monitoring.telemetry_system import telemetry; print(telemetry.get_trace(\\"{tip_trace_id}\\"))"')
    print(f"{'='*60}")

if __name__ == "__main__":
    generate_telemetry_report(days_back=1)