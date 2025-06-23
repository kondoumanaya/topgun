import json
import os
from typing import Any

import redis.asyncio as redis

from .redis_keys import RedisKeys


class BotRedisManager:
    """Bot固有のRedis管理クラス"""

    def __init__(self, bot_name: str, bot_config: dict[str, Any]):
        # 共通接続情報
        self.host = os.getenv("REDIS_HOST")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.password = os.getenv("REDIS_PASSWORD")

        # Bot固有設定
        cache_config = bot_config.get("cache", {})
        self.bot_name = bot_name
        self.ttl = cache_config.get("ttl", 60)

        self.client: redis.Redis[str] | None = None

    async def connect(self) -> None:
        """Redis接続"""
        host = self.host or "localhost"
        password = self.password or None

        self.client = redis.Redis[str](
            host=host,
            port=self.port,
            password=password,
            decode_responses=True,
        )
        await self.client.ping()

    # 市場データ系メソッド
    async def set_market_data(self, symbol: str, data: dict[str, Any], ttl: int | None = None) -> None:
        """市場データを保存"""
        key = RedisKeys.make_key(RedisKeys.MARKET_DATA, self.bot_name, symbol=symbol)
        await self._set_with_ttl(key, data, ttl)

    async def get_market_data(self, symbol: str) -> dict[str, Any] | None:
        """市場データを取得"""
        key = RedisKeys.make_key(RedisKeys.MARKET_DATA, self.bot_name, symbol=symbol)
        result = await self._get_json(key)
        if isinstance(result, dict):
            return result
        return None

    # 取引系メソッド
    async def set_last_trade(
        self, trade_id: str, trade_data: dict[str, Any], ttl: int | None = None
    ) -> None:
        """最新取引を保存"""
        key = RedisKeys.make_key(RedisKeys.LAST_TRADE, self.bot_name, trade_id=trade_id)
        await self._set_with_ttl(key, trade_data, ttl)

    async def set_position(
        self, symbol: str, position_data: dict[str, Any], ttl: int | None = None
    ) -> None:
        """ポジション情報を保存"""
        key = RedisKeys.make_key(RedisKeys.POSITION, self.bot_name, symbol=symbol)
        await self._set_with_ttl(key, position_data, ttl)

    # リスク管理系メソッド
    async def set_daily_risk_metrics(self, metrics: dict[str, Any], ttl: int = 86400) -> None:
        """日次リスク指標を保存（デフォルト24時間）"""
        key = RedisKeys.make_key(RedisKeys.RISK_METRICS_DAILY, self.bot_name)
        await self._set_with_ttl(key, metrics, ttl)

    async def get_daily_risk_metrics(self) -> dict[str, Any] | None:
        """日次リスク指標を取得"""
        key = RedisKeys.make_key(RedisKeys.RISK_METRICS_DAILY, self.bot_name)
        result = await self._get_json(key)
        if isinstance(result, dict):
            return result
        return None

    # 内部メソッド
    async def _set_with_ttl(self, key: str, value: Any, ttl: int | None = None) -> None:
        """TTL付きでデータ保存"""
        if self.client is None:
            raise RuntimeError("Redis client is not initialized. Call connect() first.")
        ttl = ttl or self.ttl
        if isinstance(value, dict | list):
            value = json.dumps(value)
        await self.client.setex(key, ttl, value)

    async def _get_json(self, key: str) -> dict[str, Any] | str | None:
        """JSONデータを取得"""
        if self.client is None:
            raise RuntimeError("Redis client is not initialized. Call connect() first.")

        value = await self.client.get(key)
        if value:
            try:
                result = json.loads(value)
                # 型チェックを追加し、戻り値型に合致させる
                if isinstance(result, dict):
                    return result  # Dict[str, Any] として返す
                if isinstance(result, str):
                    return result  # str として返す
                converted_value: str = str(result)
                return converted_value
            except json.JSONDecodeError:
                string_value: str = value
                return string_value
        return None
