# memory/graph_memory.py
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

print("="*60)
print("🧠 AGENTIC CORE - GRAPH MEMORY SYSTEM")
print("="*60)

class GraphMemory:
    """Simulated Neo4j graph database for workflow memory."""
    
    def __init__(self, db_path: str = "memory/graph_db.json"):
        self.db_path = db_path
        self.data = self._load_or_create()
        print(f"✅ Graph Memory initialized")
        print(f"   Database: {os.path.abspath(db_path)}")
        print(f"   Workflows stored: {len(self.data.get('workflows', []))}")
    
    def _load_or_create(self) -> Dict:
        """Load existing memory or create new."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    print(f"📂 Loaded existing memory: {len(data.get('workflows', []))} workflows")
                    return data
            except:
                print("⚠️  Could not load memory, creating fresh")
        
        # Create fresh structure
        return {
            "workflows": [],
            "artifacts": [],
            "agents": [],
            "relationships": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Agentic Core Graph Memory"
            }
        }
    
    def save_workflow(self, workflow: Dict[str, Any]) -> str:
        """Save a workflow to memory with relationships."""
        workflow_id = workflow.get('id', f"wf_{uuid.uuid4().hex[:8]}")
        
        # Create workflow node
        workflow_node = {
            "id": workflow_id,
            "type": "Workflow",
            "task": workflow.get('task', 'Unknown'),
            "status": workflow.get('status', 'unknown'),
            "steps_count": len(workflow.get('steps', [])),
            "created_at": workflow.get('created_at', datetime.now().isoformat()),
            "completed_at": workflow.get('completed_at'),
            "execution_time": workflow.get('result', {}).get('execution_time', '0s'),
            "node_id": f"workflow_{len(self.data['workflows']) + 1}"
        }
        
        self.data['workflows'].append(workflow_node)
        
        # Create artifact nodes for each step
        for i, step in enumerate(workflow.get('steps', []), 1):
            artifact_id = f"artifact_{uuid.uuid4().hex[:8]}"
            artifact = {
                "id": artifact_id,
                "type": "Artifact",
                "workflow_id": workflow_id,
                "step_number": i,
                "step_name": step.get('name', f'Step {i}'),
                "step_description": step.get('description', ''),
                "status": step.get('status', 'completed'),
                "timestamp": step.get('timestamp', datetime.now().isoformat()),
                "node_id": f"artifact_{len(self.data['artifacts']) + 1}"
            }
            self.data['artifacts'].append(artifact)
            
            # Create relationship
            relationship = {
                "id": f"rel_{uuid.uuid4().hex[:8]}",
                "from": workflow_node['node_id'],
                "to": artifact['node_id'],
                "type": "HAS_ARTIFACT",
                "properties": {
                    "step": i,
                    "relationship": "workflow_contains"
                }
            }
            self.data['relationships'].append(relationship)
        
        # Save to disk
        self._save()
        
        print(f"💾 Saved workflow {workflow_id} to memory")
        print(f"   Steps: {len(workflow.get('steps', []))}")
        print(f"   Status: {workflow.get('status', 'unknown')}")
        
        return workflow_id
    
    def query_workflows(self, **filters) -> List[Dict]:
        """Query workflows with optional filters."""
        results = self.data['workflows'].copy()
        
        # Apply filters
        if filters:
            filtered = []
            for workflow in results:
                match = True
                for key, value in filters.items():
                    if workflow.get(key) != value:
                        match = False
                        break
                if match:
                    filtered.append(workflow)
            results = filtered
        
        return results
    
    def get_workflow_artifacts(self, workflow_id: str) -> List[Dict]:
        """Get all artifacts for a workflow."""
        return [a for a in self.data['artifacts'] 
                if a.get('workflow_id') == workflow_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_workflows": len(self.data['workflows']),
            "total_artifacts": len(self.data['artifacts']),
            "total_relationships": len(self.data['relationships']),
            "completed_workflows": len([w for w in self.data['workflows'] 
                                       if w.get('status') == 'completed']),
            "average_steps": (
                sum(len(self.get_workflow_artifacts(w['id'])) 
                    for w in self.data['workflows']) / 
                max(1, len(self.data['workflows']))
            ),
            "memory_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }
    
    def find_similar_workflows(self, task: str, limit: int = 3) -> List[Dict]:
        """Find similar workflows based on task keywords (simple implementation)."""
        keywords = task.lower().split()
        similar = []
        
        for workflow in self.data['workflows']:
            workflow_task = workflow.get('task', '').lower()
            # Simple keyword matching
            matches = sum(1 for keyword in keywords if keyword in workflow_task)
            if matches > 0:
                similarity_score = matches / len(keywords)
                workflow_copy = workflow.copy()
                workflow_copy['similarity_score'] = similarity_score
                similar.append(workflow_copy)
        
        # Sort by similarity
        similar.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return similar[:limit]
    
    def _save(self):
        """Save memory to disk."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def clear_memory(self):
        """Clear all memory (use with caution!)."""
        self.data = {
            "workflows": [],
            "artifacts": [],
            "agents": [],
            "relationships": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Cleared and restarted"
            }
        }
        self._save()
        print("🧹 Memory cleared")

def test_graph_memory():
    """Test the graph memory system."""
    print("\n🧪 Testing Graph Memory System...")
    
    # Initialize memory
    memory = GraphMemory()
    
    # Create test workflow
    test_workflow = {
        'id': 'test_wf_123',
        'task': 'Test Python package versions',
        'status': 'completed',
        'created_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat(),
        'steps': [
            {'name': 'Research', 'description': 'Check PyPI for versions', 'status': 'completed'},
            {'name': 'Compare', 'description': 'Compare version numbers', 'status': 'completed'},
            {'name': 'Report', 'description': 'Generate summary', 'status': 'completed'}
        ],
        'result': {'execution_time': '1.5s', 'success': True}
    }
    
    # Save workflow
    memory.save_workflow(test_workflow)
    
    # Query workflows
    workflows = memory.query_workflows(status='completed')
    print(f"📊 Completed workflows: {len(workflows)}")
    
    # Get statistics
    stats = memory.get_statistics()
    print(f"📈 Memory statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Find similar workflows
    similar = memory.find_similar_workflows('Python package', limit=2)
    print(f"🔍 Similar workflows found: {len(similar)}")
    
    print("\n✅ Graph Memory System test passed!")
    return memory

if __name__ == "__main__":
    test_graph_memory()