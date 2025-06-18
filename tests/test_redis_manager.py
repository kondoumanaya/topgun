import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock redis module before importing BotRedisManager
mock_redis = MagicMock()
mock_redis.Redis = AsyncMock
sys.modules["redis"] = mock_redis
sys.modules["redis.asyncio"] = mock_redis

from shared.redis_manager import BotRedisManager  # noqa: E402


@pytest.fixture
def bot_config():
    return {"cache": {"ttl": 120}}


@pytest.fixture
def redis_manager(bot_config):
    with patch.dict(
        "os.environ",
        {
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "test_pass",
        },
    ):
        return BotRedisManager("test_bot", bot_config)


def test_redis_manager_init(redis_manager):
    """Test Redis manager initialization"""
    assert redis_manager.bot_name == "test_bot"
    assert redis_manager.ttl == 120
    assert redis_manager.host == "localhost"
    assert redis_manager.port == 6379


def test_redis_manager_init_default_ttl():
    """Test Redis manager with default TTL"""
    with patch.dict("os.environ", {"REDIS_HOST": "localhost", "REDIS_PORT": "6379"}):
        manager = BotRedisManager("default_bot", {})
        assert manager.ttl == 60


@pytest.mark.asyncio
async def test_connect(redis_manager):
    """Test Redis connection"""
    mock_client = AsyncMock()

    with patch("shared.redis_manager.redis.Redis", return_value=mock_client):
        await redis_manager.connect()

        mock_client.ping.assert_called_once()
        assert redis_manager.client == mock_client


@pytest.mark.asyncio
async def test_set_market_data(redis_manager):
    """Test setting market data"""
    redis_manager.client = AsyncMock()
    test_data = {"price": 100, "volume": 50}

    await redis_manager.set_market_data("BTC_JPY", test_data)

    redis_manager.client.setex.assert_called_once()


@pytest.mark.asyncio
async def test_get_market_data(redis_manager):
    """Test getting market data"""
    redis_manager.client = AsyncMock()
    test_data = {"price": 100, "volume": 50}
    redis_manager.client.get.return_value = json.dumps(test_data)

    result = await redis_manager.get_market_data("BTC_JPY")

    assert result == test_data
    redis_manager.client.get.assert_called_once()


@pytest.mark.asyncio
async def test_set_last_trade(redis_manager):
    """Test setting last trade"""
    redis_manager.client = AsyncMock()
    trade_data = {"id": "12345", "price": 100}

    await redis_manager.set_last_trade("12345", trade_data)

    redis_manager.client.setex.assert_called_once()


@pytest.mark.asyncio
async def test_set_position(redis_manager):
    """Test setting position"""
    redis_manager.client = AsyncMock()
    position_data = {"symbol": "BTC_JPY", "size": 0.1}

    await redis_manager.set_position("BTC_JPY", position_data)

    redis_manager.client.setex.assert_called_once()


@pytest.mark.asyncio
async def test_set_daily_risk_metrics(redis_manager):
    """Test setting daily risk metrics"""
    redis_manager.client = AsyncMock()
    metrics = {"var": 0.05, "sharpe": 1.2}

    await redis_manager.set_daily_risk_metrics(metrics)

    redis_manager.client.setex.assert_called_once()


@pytest.mark.asyncio
async def test_get_daily_risk_metrics(redis_manager):
    """Test getting daily risk metrics"""
    redis_manager.client = AsyncMock()
    metrics = {"var": 0.05, "sharpe": 1.2}
    redis_manager.client.get.return_value = json.dumps(metrics)

    result = await redis_manager.get_daily_risk_metrics()

    assert result == metrics
    redis_manager.client.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_json_none_value(redis_manager):
    """Test _get_json with None value"""
    redis_manager.client = AsyncMock()
    redis_manager.client.get.return_value = None

    result = await redis_manager._get_json("test_key")

    assert result is None


@pytest.mark.asyncio
async def test_get_json_invalid_json(redis_manager):
    """Test _get_json with invalid JSON"""
    redis_manager.client = AsyncMock()
    redis_manager.client.get.return_value = "invalid json"

    result = await redis_manager._get_json("test_key")

    assert result == "invalid json"
