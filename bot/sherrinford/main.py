#!/usr/bin/env python3
"""
Sherrinford Bot - 環境設定完全対応版 Production Ready Trading Bot
"""

import asyncio
import logging
import os
import signal
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from dotenv import load_dotenv

# プロジェクトルート特定
ROOT_DIR = Path(__file__).parent.parent.parent


# 環境設定読み込み関数
def load_environment():
    """環境設定を順序付きで読み込み"""
    print("🔧 環境設定読み込み開始...")
    print(f"📁 Project Root: {ROOT_DIR}")

    # 読み込み順序（後のファイルが優先）
    env_files = [
        ROOT_DIR / ".env",  # 1. 基本設定
        ROOT_DIR
        / f'config/{os.getenv("ENVIRONMENT", "development")}.env',  # 2. 環境固有
        ROOT_DIR / ".env.local",  # 3. 個人秘密情報
        ROOT_DIR / ".env.production",  # 4. 本番秘密情報（本番時のみ）
    ]

    loaded_files = []
    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file, override=True)  # 後のファイルで上書き
            loaded_files.append(str(env_file.name))
            print(f"✅ 設定読み込み: {env_file.name}")
        else:
            print(f"⚠️  設定ファイル不在: {env_file.name}")

    print(f"📋 読み込み完了: {', '.join(loaded_files)}")
    return loaded_files


# 環境設定読み込み実行
load_environment()

# PYTHONPATH設定
pythonpath = os.getenv("PYTHONPATH", str(ROOT_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 環境変数取得
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CONFIG_PATH = os.getenv("CONFIG_PATH", "bot/sherrinford/config.yaml")
IS_MAINNET = os.getenv("IS_MAINNET", "false").lower() == "true"
API_KEY = os.getenv("API_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# その他の設定
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "1.0"))
RISK_LIMIT = float(os.getenv("RISK_LIMIT", "0.05"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
ENABLE_PAPER_TRADING = os.getenv("ENABLE_PAPER_TRADING", "false").lower() == "true"

print(f"🌍 Environment: {ENVIRONMENT}")
print(f"📊 Log Level: {LOG_LEVEL}")
print(f"🔗 Mainnet: {IS_MAINNET}")
print(f"🔑 API Key: {'設定済み' if API_KEY else '未設定'}")
print(f"🔐 Private Key: {'設定済み' if PRIVATE_KEY else '未設定'}")
print(f"🎯 Max Position Size: {MAX_POSITION_SIZE}")
print(f"⚠️  Risk Limit: {RISK_LIMIT}")
print(f"🧪 Paper Trading: {ENABLE_PAPER_TRADING}")

try:
    # topgun ライブラリ
    from topgun.topgun.auth import Auth
    from topgun.topgun.helpers.hyperliquid import (
        construct_l1_action,
        get_timestamp_ms,
        sign_typed_data,
    )

    print("✅ topgun ライブラリインポート成功")

except ImportError as e:
    print(f"❌ topgun インポートエラー: {e}")
    print(f"📁 Python Path: {sys.path}")
    print(f"🐍 PYTHONPATH: {pythonpath}")
    raise

try:
    # 共有モジュール（存在しない場合はダミー実装）
    try:
        from shared.logger import setup_logger
    except ImportError:

        def setup_logger(name: str):
            logging.basicConfig(
                level=getattr(logging, LOG_LEVEL),
                format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            )
            return logging.getLogger(name)

    try:
        from shared.notifier import NotificationManager
    except ImportError:

        class NotificationManager:
            async def send_notification(self, title: str, message: str):
                print(f"📱 通知: {title} - {message}")

            async def send_alert(self, message: str):
                print(f"🚨 アラート: {message}")

    try:
        from shared.database import DatabaseManager
    except ImportError:

        class DatabaseManager:
            async def connect(self):
                print("🗄️ データベース接続（ダミー）")

            async def close(self):
                print("🗄️ データベース切断（ダミー）")

            async def log_order(self, order_data: dict):
                print(f"📝 注文記録: {order_data}")

    try:
        from shared.monitoring import MetricsCollector
    except ImportError:

        class MetricsCollector:
            def __init__(self, name: str):
                self.name = name

            def increment_counter(self, name: str):
                print(f"📊 カウンタ増加: {self.name}.{name}")

            def gauge(self, name: str, value):
                print(f"📊 ゲージ更新: {self.name}.{name} = {value}")

    print("✅ 共有モジュール準備完了")

except ImportError as e:
    print(f"❌ 共有モジュールインポートエラー: {e}")
    raise


@dataclass
class BotConfig:
    """ボット設定"""

    api_key: str = ""
    private_key: str = ""
    is_mainnet: bool = False
    max_position_size: float = 1.0
    risk_limit: float = 0.05
    symbols: list[str] = field(default_factory=lambda: ["BTC", "ETH"])
    enable_paper_trading: bool = False

    def __post_init__(self):
        # 環境変数から設定を取得（優先）
        self.api_key = API_KEY or self.api_key
        self.private_key = PRIVATE_KEY or self.private_key
        self.is_mainnet = IS_MAINNET
        self.max_position_size = MAX_POSITION_SIZE
        self.risk_limit = RISK_LIMIT
        self.enable_paper_trading = ENABLE_PAPER_TRADING


class SherrinfordBot:
    """Sherrinford Trading Bot - 環境設定完全対応版"""

    def __init__(self, config_path: str | None = None):
        # ログ設定
        self.logger = setup_logger("sherrinford")
        self.logger.info("🚀 Sherrinford Bot 初期化開始")
        self.logger.info(f"📁 Root Directory: {ROOT_DIR}")
        self.logger.info(f"🌍 Environment: {ENVIRONMENT}")
        self.logger.info(f"📊 Log Level: {LOG_LEVEL}")

        # 設定読み込み
        self.config = self._load_config(config_path or CONFIG_PATH)

        # 各種マネージャー初期化
        self.auth = Auth()
        self.notifier = NotificationManager()
        self.db = DatabaseManager()
        self.metrics = MetricsCollector("sherrinford")

        # 状態管理
        self.is_running = False
        self.positions = {}
        self.last_heartbeat = datetime.now()
        self.order_count = 0
        self.error_count = 0

        # シグナルハンドラ設定
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.logger.info("✅ Sherrinford Bot 初期化完了")

    def _load_config(self, config_path: str) -> BotConfig:
        """設定ファイル読み込み"""
        self.logger.info(f"📝 設定ファイル読み込み: {config_path}")

        try:
            config_file = ROOT_DIR / config_path

            if config_file.exists():
                with open(config_file, encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
                self.logger.info("✅ 設定ファイル読み込み成功")
            else:
                self.logger.warning(f"⚠️ 設定ファイルが存在しません: {config_file}")
                config_data = {}

            # 設定オブジェクト作成（環境変数が優先）
            config = BotConfig(**config_data)

            # 設定内容ログ出力（秘密情報を除く）
            self.logger.info("📊 設定内容:")
            self.logger.info(f"   Environment: {ENVIRONMENT}")
            self.logger.info(f"   is_mainnet: {config.is_mainnet}")
            self.logger.info(f"   max_position_size: {config.max_position_size}")
            self.logger.info(f"   risk_limit: {config.risk_limit}")
            self.logger.info(f"   symbols: {config.symbols}")
            self.logger.info(f"   enable_paper_trading: {config.enable_paper_trading}")
            self.logger.info(
                f"   api_key: {'設定済み' if config.api_key else '未設定'}"
            )
            self.logger.info(
                f"   private_key: {'設定済み' if config.private_key else '未設定'}"
            )

            return config

        except Exception as e:
            self.logger.error(f"❌ 設定ファイル読み込みエラー: {e}")
            # デフォルト設定で継続
            self.logger.info("🔄 デフォルト設定で継続")
            return BotConfig()

    def _signal_handler(self, signum, frame):
        """シグナルハンドラ"""
        self.logger.info(f"📡 シグナル {signum} を受信。シャットダウン開始...")
        self.is_running = False

    async def create_order(
        self, symbol: str, side: str, quantity: float, price: float
    ) -> dict | None:
        """注文作成"""
        try:
            self.logger.info(f"📋 注文作成開始: {symbol} {side} {quantity}@{price}")

            # Paper Trading チェック
            if self.config.enable_paper_trading:
                self.logger.info("🧪 Paper Trading モード - 実際の注文は行いません")
                await self._simulate_order(symbol, side, quantity, price)
                return {"simulation": True, "symbol": symbol, "side": side}

            # リスク管理チェック
            if not self._risk_check(symbol, quantity):
                self.logger.warning(f"⚠️ リスク管理により注文拒否: {symbol} {quantity}")
                return None

            # 秘密鍵チェック
            if not self.config.private_key:
                self.logger.error("❌ private_key が設定されていません")
                return None

            # L1アクション構築
            action = {
                "type": "order",
                "orders": [
                    {
                        "asset": symbol,
                        "isBuy": side == "buy",
                        "sz": str(quantity),
                        "limitPx": str(price),
                        "orderType": {"limit": {"tif": "Gtc"}},
                    }
                ],
            }

            # EIP-712データ構築
            nonce = get_timestamp_ms()
            domain, types, message = construct_l1_action(
                action, nonce, self.config.is_mainnet
            )

            self.logger.debug("🔐 EIP-712データ構築完了")

            # 署名
            signature = sign_typed_data(self.config.private_key, domain, types, message)

            # データベース記録
            await self.db.log_order(
                {
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "price": price,
                    "signature": signature,
                    "timestamp": datetime.now(),
                    "environment": ENVIRONMENT,
                    "paper_trading": self.config.enable_paper_trading,
                }
            )

            # メトリクス更新
            self.metrics.increment_counter("orders_created")
            self.order_count += 1

            self.logger.info(f"✅ 注文作成完了: {symbol} {side} {quantity}@{price}")
            return signature

        except Exception as e:
            self.logger.error(f"❌ 注文作成エラー: {e}", exc_info=True)
            self.metrics.increment_counter("orders_failed")
            self.error_count += 1
            await self.notifier.send_alert(f"注文エラー: {e}")
            return None

    async def _simulate_order(
        self, symbol: str, side: str, quantity: float, price: float
    ):
        """Paper Trading用の注文シミュレーション"""
        self.logger.info(f"🧪 シミュレーション注文: {symbol} {side} {quantity}@{price}")

        # シミュレーション用の遅延
        await asyncio.sleep(0.1)

        # ポジション更新（シミュレーション）
        current_position = self.positions.get(symbol, 0)
        new_position = current_position + (quantity if side == "buy" else -quantity)
        self.positions[symbol] = new_position

        self.logger.info(
            f"📊 {symbol} ポジション更新: {current_position} → {new_position}"
        )

    def _risk_check(self, symbol: str, quantity: float) -> bool:
        """リスク管理チェック"""
        try:
            # ポジションサイズチェック
            current_position = self.positions.get(symbol, 0)
            new_position = abs(current_position + quantity)

            if new_position > self.config.max_position_size:
                self.logger.warning(
                    f"⚠️ ポジションサイズ制限: {new_position} > {self.config.max_position_size}"
                )
                return False

            # 環境別制限
            if (
                ENVIRONMENT == "development" and quantity > 0.01
            ):  # 開発環境では小額に制限
                self.logger.warning(f"⚠️ 開発環境での量制限: {quantity} > 0.01")
                return False

            # エラー頻発時の取引停止
            if self.error_count > 10:
                self.logger.warning(
                    f"⚠️ エラー頻発により取引停止: {self.error_count} errors"
                )
                return False

            # その他のリスクチェック
            # - 最大ドローダウン
            # - 日次取引限度
            # - 市場時間チェック

            return True

        except Exception as e:
            self.logger.error(f"❌ リスクチェックエラー: {e}")
            return False

    async def update_positions(self):
        """ポジション更新"""
        try:
            # APIからポジション情報取得（実装予定）
            if self.config.api_key and not self.config.enable_paper_trading:
                # 実際のAPI呼び出し
                # positions = await self.get_positions_from_api()
                # self.positions.update(positions)
                pass

            # メトリクス更新
            self.metrics.gauge("total_positions", len(self.positions))
            self.metrics.gauge("order_count", self.order_count)
            self.metrics.gauge("error_count", self.error_count)

            if self.positions and DEBUG_MODE:
                self.logger.debug(f"📊 現在のポジション: {self.positions}")

        except Exception as e:
            self.logger.error(f"❌ ポジション更新エラー: {e}")

    async def heartbeat(self):
        """ヘルスチェック用ハートビート"""
        try:
            self.last_heartbeat = datetime.now()
            self.metrics.gauge("last_heartbeat", self.last_heartbeat.timestamp())

            # 長時間応答なしの場合アラート
            if datetime.now() - self.last_heartbeat > timedelta(minutes=5):
                await self.notifier.send_alert("ボットが応答しません")

            # 定期的なハートビートログ（開発環境のみ）
            if ENVIRONMENT == "development" and DEBUG_MODE:
                self.logger.debug(f"💓 ハートビート: {self.last_heartbeat}")

        except Exception as e:
            self.logger.error(f"❌ ハートビートエラー: {e}")

    async def run(self):
        """メインループ"""
        self.logger.info("🚀 Sherrinford Bot メインループ開始")
        self.is_running = True

        # 初期状態確認
        await self._initial_checks()

        try:
            # 初期化処理
            await self.db.connect()
            await self.notifier.send_notification(
                "ボット開始",
                f"Sherrinford Bot が開始されました\n"
                f"Environment: {ENVIRONMENT}\n"
                f"Paper Trading: {self.config.enable_paper_trading}\n"
                f"Mainnet: {self.config.is_mainnet}",
            )

            # メインループ
            loop_count = 0
            while self.is_running:
                try:
                    loop_count += 1

                    # ハートビート
                    await self.heartbeat()

                    # ポジション更新
                    await self.update_positions()

                    # 取引ロジック実行
                    await self.execute_trading_logic()

                    # 定期ログ（開発環境）
                    if ENVIRONMENT == "development" and loop_count % 60 == 0:
                        self.logger.info(f"🔄 メインループ実行中: {loop_count}回")
                        self.logger.info(
                            f"📊 統計: 注文{self.order_count}回, エラー{self.error_count}回"
                        )

                    # 待機
                    await asyncio.sleep(1)

                except KeyboardInterrupt:
                    self.logger.info("⌨️ キーボード割り込み受信")
                    break
                except Exception as e:
                    self.logger.error(f"❌ メインループエラー: {e}", exc_info=True)
                    self.error_count += 1
                    await self.notifier.send_alert(f"メインループエラー: {e}")
                    await asyncio.sleep(5)  # エラー時は長めに待機

        except Exception as e:
            self.logger.error(f"❌ 致命的エラー: {e}", exc_info=True)
            await self.notifier.send_alert(f"致命的エラー: {e}")

        finally:
            # クリーンアップ
            await self._cleanup()

    async def _initial_checks(self):
        """初期状態確認"""
        self.logger.info("🔍 初期状態確認中...")

        # topgun ライブラリテスト
        try:
            timestamp = get_timestamp_ms()
            self.logger.info(f"⏰ 現在のタイムスタンプ: {timestamp}")
        except Exception as e:
            self.logger.error(f"❌ topgun ライブラリテストエラー: {e}")

        # 設定確認
        if not self.config.api_key and ENVIRONMENT == "production":
            self.logger.warning("⚠️ API_KEY が本番環境で未設定")

        if not self.config.private_key and not self.config.enable_paper_trading:
            self.logger.warning("⚠️ PRIVATE_KEY が未設定（Paper Tradingが無効）")

        # 環境固有チェック
        if ENVIRONMENT == "production" and self.config.enable_paper_trading:
            self.logger.warning("⚠️ 本番環境でPaper Tradingが有効")

        if ENVIRONMENT == "development" and self.config.is_mainnet:
            self.logger.warning("⚠️ 開発環境でMainnetが有効")

        self.logger.info("✅ 初期状態確認完了")

    async def execute_trading_logic(self):
        """取引ロジック実行"""
        try:
            # 開発環境でのサンプル取引ロジック
            if ENVIRONMENT == "development":
                # 10分に1回サンプル注文作成
                current_minute = datetime.now().minute
                current_second = datetime.now().second

                if current_minute % 10 == 0 and current_second < 2:
                    self.logger.info("📊 サンプル取引ロジック実行")

                    # デモ注文データ
                    sample_order = await self.create_order("BTC", "buy", 0.001, 50000.0)
                    if sample_order:
                        self.logger.info(f"✅ サンプル注文作成: {sample_order}")

            # ここに実際の取引戦略を実装
            # - マーケットデータ取得
            # - シグナル計算
            # - 注文実行

        except Exception as e:
            self.logger.error(f"❌ 取引ロジックエラー: {e}")

    async def _cleanup(self):
        """クリーンアップ処理"""
        self.logger.info("🧹 クリーンアップ開始...")

        try:
            # データベース接続クローズ
            await self.db.close()

            # メトリクス最終更新
            self.metrics.gauge("bot_status", 0)  # 停止状態

            # 最終統計
            self.logger.info("📊 最終統計:")
            self.logger.info(f"   注文回数: {self.order_count}")
            self.logger.info(f"   エラー回数: {self.error_count}")
            self.logger.info(f"   ポジション数: {len(self.positions)}")

            # 最終通知
            await self.notifier.send_notification(
                "ボット停止",
                f"Sherrinford Bot が停止しました\n"
                f"Environment: {ENVIRONMENT}\n"
                f"注文回数: {self.order_count}\n"
                f"エラー回数: {self.error_count}",
            )

        except Exception as e:
            self.logger.error(f"❌ クリーンアップエラー: {e}")

        self.logger.info("✅ クリーンアップ完了")


async def main():
    """メイン関数"""
    print(f"🚀 Sherrinford Bot 起動 (Environment: {ENVIRONMENT})")
    print(f"🧪 Paper Trading: {ENABLE_PAPER_TRADING}")
    print(f"🔗 Mainnet: {IS_MAINNET}")

    try:
        bot = SherrinfordBot()
        await bot.run()
    except KeyboardInterrupt:
        print("⌨️ キーボード割り込みによる終了")
    except Exception as e:
        print(f"❌ 起動エラー: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("👋 Sherrinford Bot 終了")


if __name__ == "__main__":
    asyncio.run(main())
