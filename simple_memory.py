import json
import os
import hashlib
from datetime import datetime

class SimpleMemory:
    def __init__(self):
        os.makedirs("artifacts", exist_ok=True)
        print("✅ Memory ready")

    def store(self, task, result):
        artifact_id = f"artifact_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        data = {
            "id": artifact_id,
            "task": task,
            "result": result,
            "hash": hashlib.sha256(str(result).encode()).hexdigest()[:16],
            "timestamp": datetime.now().isoformat()
        }
        with open(f"artifacts/{artifact_id}.json", 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Stored: {artifact_id}")
        return artifact_id

    def get_stats(self):
        if not os.path.exists("artifacts"):
            return {"total": 0}
        files = [f for f in os.listdir("artifacts") if f.endswith('.json')]
        return {"total": len(files)}