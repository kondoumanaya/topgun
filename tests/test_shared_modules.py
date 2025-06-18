import tempfile
from pathlib import Path
from unittest.mock import patch

from shared.logger import setup_logger
from shared.redis_keys import RedisKeys


def test_logger_file_handler_creation():
    """Test that file handler is created with correct settings"""
    with (
        tempfile.TemporaryDirectory() as temp_dir,
        patch("shared.logger.Path") as mock_path,
    ):
        mock_log_dir = Path(temp_dir) / "logs"
        mock_path.return_value = mock_log_dir

        logger = setup_logger("file_test_bot")

        assert len(logger.handlers) == 2
        file_handler = logger.handlers[1]
        assert hasattr(file_handler, "maxBytes")
        assert hasattr(file_handler, "backupCount")


def test_logger_formatter():
    """Test logger formatter configuration"""
    logger = setup_logger("format_test_bot")

    for handler in logger.handlers:
        formatter = handler.formatter
        assert formatter is not None
        assert "%(asctime)s" in formatter._fmt
        assert "%(name)s" in formatter._fmt
        assert "%(levelname)s" in formatter._fmt


def test_redis_keys_all_templates():
    """Test all Redis key templates"""
    templates = [
        (RedisKeys.MARKET_DATA, {"symbol": "BTC_JPY"}),
        (RedisKeys.TICKER_DATA, {"symbol": "ETH_JPY"}),
        (RedisKeys.ORDERBOOK, {"symbol": "BTC_USD"}),
        (RedisKeys.LAST_TRADE, {"trade_id": "12345"}),
        (RedisKeys.POSITION, {"symbol": "ETH_USD"}),
        (RedisKeys.ORDERS_PENDING, {"order_id": "67890"}),
        (RedisKeys.RISK_METRICS_DAILY, {}),
        (RedisKeys.RISK_METRICS_HOURLY, {}),
        (RedisKeys.DAILY_PNL, {}),
        (RedisKeys.SIGNALS_TREND, {"direction": "up"}),
        (RedisKeys.SIGNALS_MOMENTUM, {}),
        (RedisKeys.ARBITRAGE_SPREAD, {"symbol": "BTC"}),
        (RedisKeys.SCALPING_OPPORTUNITY, {"symbol": "ETH"}),
    ]

    for template, kwargs in templates:
        key = RedisKeys.make_key(template, "test_bot", **kwargs)
        assert "test_bot" in key
        assert key.startswith("test_bot:")


def test_redis_keys_complex_formatting():
    """Test Redis keys with complex parameter combinations"""
    key = RedisKeys.make_key(
        RedisKeys.SIGNALS_TREND, "complex_bot", direction="bullish_trend"
    )
    assert key == "complex_bot:signals:trend_bullish_trend"

    key = RedisKeys.make_key(RedisKeys.ARBITRAGE_SPREAD, "arb_bot_v2", symbol="BTC_ETH")
    assert key == "arb_bot_v2:arbitrage:BTC_ETH_spread"
