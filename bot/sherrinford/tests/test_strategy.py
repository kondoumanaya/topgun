import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

def test_basic_imports() -> None:
    """Test that basic modules can be imported without errors."""
    from shared.redis_keys import RedisKeys
    from shared.redis_manager import BotRedisManager
    
    key = RedisKeys.make_key(RedisKeys.MARKET_DATA, "test_bot", symbol="BTC")
    assert "test_bot" in key
    assert "BTC" in key
    
    config = {"cache": {"ttl": 60}}
    manager = BotRedisManager("test_bot", config)
    assert manager.bot_name == "test_bot"
    assert manager.ttl == 60

def test_redis_keys() -> None:
    """Test RedisKeys utility functions."""
    from shared.redis_keys import RedisKeys
    
    key = RedisKeys.make_key(RedisKeys.POSITION, "sherrinford", symbol="ETH")
    assert isinstance(key, str)
    assert len(key) > 0
    
    market_key = RedisKeys.make_key(RedisKeys.MARKET_DATA, "watson", symbol="BTC")
    trade_key = RedisKeys.make_key(RedisKeys.LAST_TRADE, "watson", trade_id="123")
    
    assert market_key != trade_key
    assert "watson" in market_key
    assert "watson" in trade_key
