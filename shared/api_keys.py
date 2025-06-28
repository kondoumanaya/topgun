"""共通APIキー管理モジュール
各ボットで使用するAPIキーを一元管理します。
環境変数から読み込み、安全に各ボットに提供します。
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class APIKeyManager:
    """APIキー管理クラス"""

    def __init__(self):
        load_dotenv("env/.env.local")
        load_dotenv("env/.env")
        load_dotenv("env/.env.production")
        load_dotenv("env/.env.example")

        self._keys: Dict[str, Optional[str]] = {}
        self._load_api_keys()

    def _load_api_keys(self) -> None:
        """環境変数からAPIキーを読み込み"""
        self._keys["gmo_api_key"] = os.getenv("GMO_API_KEY")
        self._keys["gmo_secret_key"] = os.getenv("GMO_SECRET_KEY")

        self._keys["binance_api_key"] = os.getenv("BINANCE_API_KEY")
        self._keys["binance_secret_key"] = os.getenv("BINANCE_SECRET_KEY")

        self._keys["okx_api_key"] = os.getenv("OKX_API_KEY")
        self._keys["okx_secret_key"] = os.getenv("OKX_SECRET_KEY")

        self._keys["slack_webhook"] = os.getenv("SLACK_WEBHOOK_URL")
        self._keys["discord_webhook"] = os.getenv("DISCORD_WEBHOOK_URL")

        self._keys["db_password"] = os.getenv("DB_PASSWORD")
        self._keys["redis_password"] = os.getenv("REDIS_PASSWORD")

    def get_gmo_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """GMOコインのAPIキーを取得"""
        return self._keys.get("gmo_api_key"), self._keys.get("gmo_secret_key")

    def get_binance_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """BinanceのAPIキーを取得"""
        return (self._keys.get("binance_api_key"), 
                self._keys.get("binance_secret_key"))

    def get_notification_webhooks(self) -> Dict[str, Optional[str]]:
        """通知用WebhookURLを取得"""
        return {
            "slack": self._keys.get("slack_webhook"),
            "discord": self._keys.get("discord_webhook")
        }

    def get_database_credentials(self) -> Dict[str, Optional[str]]:
        """データベース認証情報を取得"""
        return {
            "db_password": self._keys.get("db_password"),
            "redis_password": self._keys.get("redis_password")
        }

    def validate_keys(self, required_keys: list[str]) -> bool:
        """必要なAPIキーが設定されているかチェック"""
        missing_keys = []
        for key in required_keys:
            if not self._keys.get(key):
                missing_keys.append(key)

        if missing_keys:
            logger.error(f"Missing required API keys: {missing_keys}")
            return False

        return True


api_keys = APIKeyManager()
