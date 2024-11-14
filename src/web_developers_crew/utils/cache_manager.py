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

    def cache_agent_output(self, agent_name: str, output: str) -> bool:
        """Cache the output from an agent"""
        try:
            logger.info(f"Attempting to cache output for {agent_name}")
            logger.debug(f"Cache file path: {self.cache_file}")

            # Read existing cache
            if self.cache_file.exists():
                cache_data = json.loads(self.cache_file.read_text())
            else:
                logger.warning("Cache file not found, creating new one")
                cache_data = {}

            # Update cache
            cache_data[agent_name] = output

            # Write with pretty printing for debugging
            self.cache_file.write_text(json.dumps(cache_data, indent=2))
            logger.info(f"Wrote cache data for {agent_name}")

            # Verify write
            new_cache_data = json.loads(self.cache_file.read_text())
            if agent_name in new_cache_data:
                logger.info(f"Successfully verified cache write for {agent_name}")
                return True
            else:
                logger.error(f"Failed to verify cache write for {agent_name}")
                return False

        except Exception as e:
            logger.error(f"Error caching output for {agent_name}: {e}")
            logger.exception("Full traceback:")
            return False

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

    def clear(self):
        """Clear the cache file"""
        try:
            self.cache_data = {}
            self._write_cache()
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return False
