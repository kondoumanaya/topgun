from shared.redis_keys import RedisKeys


def test_make_key_basic():
    """Test basic key generation"""
    key = RedisKeys.make_key(RedisKeys.MARKET_DATA, "test_bot", symbol="BTC_JPY")
    assert key == "test_bot:market_data:BTC_JPY"


def test_make_key_with_multiple_params():
    """Test key generation with multiple parameters"""
    key = RedisKeys.make_key(RedisKeys.LAST_TRADE, "trading_bot", trade_id="12345")
    assert key == "trading_bot:last_trade:12345"


def test_make_key_position():
    """Test position key generation"""
    key = RedisKeys.make_key(RedisKeys.POSITION, "arb_bot", symbol="ETH_JPY")
    assert key == "arb_bot:position:ETH_JPY"


def test_make_key_risk_metrics():
    """Test risk metrics key generation"""
    key = RedisKeys.make_key(RedisKeys.RISK_METRICS_DAILY, "risk_bot")
    assert key == "risk_bot:risk_metrics:daily"


def test_make_key_ticker_data():
    """Test ticker data key generation"""
    key = RedisKeys.make_key(RedisKeys.TICKER_DATA, "ticker_bot", symbol="BTC_USD")
    assert key == "ticker_bot:ticker:BTC_USD"


def test_make_key_orderbook():
    """Test orderbook key generation"""
    key = RedisKeys.make_key(RedisKeys.ORDERBOOK, "ob_bot", symbol="ETH_USD")
    assert key == "ob_bot:orderbook:ETH_USD"


def test_make_key_signals_trend():
    """Test signals trend key generation"""
    key = RedisKeys.make_key(RedisKeys.SIGNALS_TREND, "signal_bot", direction="up")
    assert key == "signal_bot:signals:trend_up"


def test_make_key_arbitrage_spread():
    """Test arbitrage spread key generation"""
    key = RedisKeys.make_key(RedisKeys.ARBITRAGE_SPREAD, "arb_bot", symbol="BTC")
    assert key == "arb_bot:arbitrage:BTC_spread"
