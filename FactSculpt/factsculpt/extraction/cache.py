"""
factsculpt/extraction/cache.py
Persistent, thread-safe disk cache for LLM extraction responses.
Prevents duplicate API/inference calls for identical texts, ensuring idempotency and speed.
"""

import os
import json
import hashlib
import threading
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "cache"
)


class ProfileResponseCache:
    """
    Disk-backed persistent cache for evidence extraction profiles.
    Keyed by SHA-256 of (model_name + "::" + text).
    """

    def __init__(self, cache_file: Optional[str] = None):
        if cache_file is None:
            os.makedirs(DEFAULT_CACHE_DIR, exist_ok=True)
            self.cache_file = os.path.join(DEFAULT_CACHE_DIR, "extractor_profile_cache.json")
        else:
            self.cache_file = cache_file
            os.makedirs(os.path.dirname(os.path.abspath(cache_file)), exist_ok=True)

        self._lock = threading.Lock()
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._dirty_count = 0
        self._load_cache()

        import atexit
        atexit.register(self.flush)

    def _compute_key(self, text: str, model_name: str) -> str:
        norm_text = text.strip().lower()
        content = f"{model_name.strip()}::{norm_text}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _load_cache(self):
        with self._lock:
            if os.path.exists(self.cache_file):
                try:
                    with open(self.cache_file, "r", encoding="utf-8") as f:
                        self._memory_cache = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not load cache file {self.cache_file}: {e}")
                    self._memory_cache = {}
            else:
                self._memory_cache = {}

    def get(self, text: str, model_name: str) -> Optional[Dict[str, Any]]:
        key = self._compute_key(text, model_name)
        with self._lock:
            return self._memory_cache.get(key)

    def set(self, text: str, model_name: str, profile_data: Dict[str, Any]):
        key = self._compute_key(text, model_name)
        with self._lock:
            self._memory_cache[key] = profile_data
            self._dirty_count += 1
            if self._dirty_count >= 250:
                self._save_to_disk()

    def flush(self):
        with self._lock:
            if self._dirty_count > 0:
                self._save_to_disk()

    def _save_to_disk(self):
        try:
            temp_file = f"{self.cache_file}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._memory_cache, f)
            os.replace(temp_file, self.cache_file)
            self._dirty_count = 0
        except Exception as e:
            logger.warning(f"Could not write cache file {self.cache_file}: {e}")

    def clear(self):
        with self._lock:
            self._memory_cache = {}
            self._dirty_count = 0
            if os.path.exists(self.cache_file):
                try:
                    os.remove(self.cache_file)
                except Exception:
                    pass

    def __len__(self) -> int:
        with self._lock:
            return len(self._memory_cache)
