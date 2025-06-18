import json
import os
from typing import Any

import redis.asyncio as redis

from .redis_keys import RedisKeys


class BotRedisManager:
    """Bot固有のRedis管理クラス"""

    def __init__(self, bot_name: str, bot_config: dict):
        # 共通接続情報
        self.host = os.getenv("REDIS_HOST")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.password = os.getenv("REDIS_PASSWORD")

        # Bot固有設定
        cache_config = bot_config.get("cache", {})
        self.bot_name = bot_name
        self.ttl = cache_config.get("ttl", 60)

        self.client: redis.Redis | None = None

    async def connect(self):
        """Redis接続"""
        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            decode_responses=True,
        )
        await self.client.ping()

    # 市場データ系メソッド
    async def set_market_data(self, symbol: str, data: dict, ttl: int | None = None):
        """市場データを保存"""
        key = RedisKeys.make_key(RedisKeys.MARKET_DATA, self.bot_name, symbol=symbol)
        await self._set_with_ttl(key, data, ttl)

    async def get_market_data(self, symbol: str) -> dict | None:
        """市場データを取得"""
        key = RedisKeys.make_key(RedisKeys.MARKET_DATA, self.bot_name, symbol=symbol)
        return await self._get_json(key)

    # 取引系メソッド
    async def set_last_trade(
        self, trade_id: str, trade_data: dict, ttl: int | None = None
    ):
        """最新取引を保存"""
        key = RedisKeys.make_key(RedisKeys.LAST_TRADE, self.bot_name, trade_id=trade_id)
        await self._set_with_ttl(key, trade_data, ttl)

    async def set_position(
        self, symbol: str, position_data: dict, ttl: int | None = None
    ):
        """ポジション情報を保存"""
        key = RedisKeys.make_key(RedisKeys.POSITION, self.bot_name, symbol=symbol)
        await self._set_with_ttl(key, position_data, ttl)

    # リスク管理系メソッド
    async def set_daily_risk_metrics(self, metrics: dict, ttl: int = 86400):
        """日次リスク指標を保存（デフォルト24時間）"""
        key = RedisKeys.make_key(RedisKeys.RISK_METRICS_DAILY, self.bot_name)
        await self._set_with_ttl(key, metrics, ttl)

    async def get_daily_risk_metrics(self) -> dict | None:
        """日次リスク指標を取得"""
        key = RedisKeys.make_key(RedisKeys.RISK_METRICS_DAILY, self.bot_name)
        return await self._get_json(key)

    # 内部メソッド
    async def _set_with_ttl(self, key: str, value: Any, ttl: int | None = None):
        """TTL付きでデータ保存"""
        ttl = ttl or self.ttl
        if isinstance(value, dict | list):
            value = json.dumps(value)
        await self.client.setex(key, ttl, value)

    async def _get_json(self, key: str) -> Any:
        """JSONデータを取得"""
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
