import os
import json
from typing import Dict, Optional


class CacheManager:
    def __init__(self, topic: str):
        self.topic = topic
        self.cache_dir = os.path.join("output", topic.lower())
        os.makedirs(self.cache_dir, exist_ok=True)

    def cache_agent_output(self, agent_name: str, output: str):
        """Cache an agent's output"""
        cache_file = os.path.join(self.cache_dir, f"{agent_name}.json")
        with open(cache_file, "w") as f:
            json.dump({"output": output}, f)

    def get_agent_output(self, agent_name: str) -> Optional[str]:
        """Retrieve an agent's cached output"""
        cache_file = os.path.join(self.cache_dir, f"{agent_name}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                data = json.load(f)
                return data.get("output")
        return None
