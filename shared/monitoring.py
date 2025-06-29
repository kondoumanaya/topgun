"""Monitoring and metrics collection for trading bots"""
import logging
from typing import Dict, Any
import time

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and manages bot metrics"""

    def __init__(self, name: str):
        self.name = name
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.start_time: float = time.time()

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric"""
        self.counters[name] = self.counters.get(name, 0) + value
        logger.debug(f"📊 Counter {self.name}.{name}: {self.counters[name]}")

    def gauge(self, name: str, value: float) -> None:
        """Set a gauge metric"""
        self.gauges[name] = value
        logger.debug(f"📊 Gauge {self.name}.{name}: {value}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        return {
            "counters": self.counters.copy(),
            "gauges": self.gauges.copy(),
            "uptime": time.time() - self.start_time
        }

    def reset_counters(self) -> None:
        """Reset all counters"""
        self.counters.clear()
        logger.info(f"📊 Reset counters for {self.name}")
