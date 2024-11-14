import logging
import os
import json
from typing import Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, topic: str):
        self.cache_dir = Path(".cache")
        self.topic = topic
        self.cache_file = self.cache_dir / f"{topic.lower()}_cache.json"

        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)

        # Initialize cache file if it doesn't exist
        if not self.cache_file.exists():
            self.cache_file.write_text("{}")

        logger.info(f"Initialized cache for topic: {topic}")

    def cache_agent_output(self, agent_name: str, output: str) -> None:
        """Cache the output from an agent"""
        try:
            logger.info(f"Attempting to cache output for {agent_name}")
            logger.debug(f"Cache file path: {self.cache_file}")

            cache_data = json.loads(self.cache_file.read_text())
            cache_data[agent_name] = output

            # Write with pretty printing for debugging
            self.cache_file.write_text(json.dumps(cache_data, indent=2))

            # Verify write
            if agent_name in json.loads(self.cache_file.read_text()):
                logger.info(f"Successfully cached output for agent: {agent_name}")
            else:
                logger.error(f"Failed to verify cache write for: {agent_name}")

        except Exception as e:
            logger.error(f"Error caching output for {agent_name}: {e}")
            logger.exception("Full traceback:")

    def get_agent_output(self, agent_name: str) -> Optional[str]:
        """Get cached output for an agent"""
        try:
            cache_data = json.loads(self.cache_file.read_text())
            if agent_name not in cache_data:
                logger.warning(f"No cached output found for agent: {agent_name}")
                return None
            return cache_data[agent_name]
        except Exception as e:
            logger.error(f"Error reading cache for {agent_name}: {e}")
            return None
