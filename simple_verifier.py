import hashlib

class SimpleVerifier:
    def verify(self, task, result):
        # Simple 3-agent mock verification
        agents = ["Agent1", "Agent2", "Agent3"]
        votes = []
        for agent in agents:
            votes.append({"agent": agent, "vote": "accept", "reason": "Looks good"})

        verification_hash = hashlib.sha256(f"{task}{str(result)}".encode()).hexdigest()

        return {
            "status": "TRIPLE_VERIFIED",
            "confidence": 0.99,
            "hash": verification_hash,
            "agents": votes
        }