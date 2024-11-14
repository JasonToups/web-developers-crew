import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def inspect_cache(topic: str = "Books") -> None:
    """Inspect the cache contents for a given topic"""
    cache_dir = Path(".cache")
    cache_file = cache_dir / f"{topic.lower()}_cache.json"

    if not cache_file.exists():
        logger.error(f"No cache file found for topic: {topic}")
        return

    try:
        cache_data = json.loads(cache_file.read_text())
        print(f"\nCache contents for topic '{topic}':")
        print("-" * 50)

        if not cache_data:
            print("Cache is empty!")
            return

        for agent, output in cache_data.items():
            print(f"\nAgent: {agent}")
            print("Output length:", len(str(output)))
            print("First 100 chars:", str(output)[:100] + "...")
            print("-" * 50)

    except Exception as e:
        logger.error(f"Error reading cache: {e}")
