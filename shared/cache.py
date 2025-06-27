"""Cache utilities for trading bots"""
import asyncio
from typing import Any, Optional, Dict
import json
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """Simple in-memory cache with TTL support"""

    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
        self.default_ttl = default_ttl

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            if asyncio.get_event_loop().time() < self._ttl.get(key, 0):
                return self._cache[key]
            else:
                del self._cache[key]
                del self._ttl[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        self._cache[key] = value
        expire_time = asyncio.get_event_loop().time() + (ttl or self.default_ttl)
        self._ttl[key] = expire_time