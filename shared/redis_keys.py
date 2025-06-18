class RedisKeys:
    """Redis キーテンプレートの定義"""

    # 市場データ系
    MARKET_DATA = "{bot_name}:market_data:{symbol}"
    TICKER_DATA = "{bot_name}:ticker:{symbol}"
    ORDERBOOK = "{bot_name}:orderbook:{symbol}"

    # 取引系
    LAST_TRADE = "{bot_name}:last_trade:{trade_id}"
    POSITION = "{bot_name}:position:{symbol}"
    ORDERS_PENDING = "{bot_name}:orders:pending:{order_id}"

    # リスク管理系
    RISK_METRICS_DAILY = "{bot_name}:risk_metrics:daily"
    RISK_METRICS_HOURLY = "{bot_name}:risk_metrics:hourly"
    DAILY_PNL = "{bot_name}:daily_pnl"

    # シグナル系
    SIGNALS_TREND = "{bot_name}:signals:trend_{direction}"
    SIGNALS_MOMENTUM = "{bot_name}:signals:momentum"

    # Bot固有キー
    ARBITRAGE_SPREAD = "{bot_name}:arbitrage:{symbol}_spread"
    SCALPING_OPPORTUNITY = "{bot_name}:scalping:{symbol}"

    @classmethod
    def make_key(cls, template: str, bot_name: str, **kwargs) -> str:
        """キーテンプレートから実際のキーを生成"""
        return template.format(bot_name=bot_name, **kwargs)
