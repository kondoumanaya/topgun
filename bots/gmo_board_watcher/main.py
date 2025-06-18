#!/usr/bin/env python3

import asyncio
import logging
import os
import sys
from contextlib import suppress
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "topgun"))

from topgun import Client, GMOCoinDataStore

with suppress(ImportError):
    from rich import print

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class GMOBoardWatcher:
    def __init__(self, symbol: str = "BTC_JPY") -> None:
        self.symbol = symbol
        self.client: Optional[Client] = None
        self.store: Optional[GMOCoinDataStore] = None
        self.running = False

    async def start(self) -> None:
        self.client = Client()
        self.store = GMOCoinDataStore()

        try:
            await self.client.ws_connect(
                "wss://api.coin.z.com/ws/public/v1",
                send_json={
                    "command": "subscribe",
                    "channel": "orderbooks",
                    "symbol": self.symbol,
                },
                hdlr_json=self.store.onmessage,
            )

            self.running = True
            logger.info(f"Started watching GMO Coin board data for {self.symbol}")

            while self.running:
                if self.store is not None:
                    orderbook = self.store.orderbooks.sorted(limit=5)
                    if orderbook:
                        print(f"[{self.symbol}] Board Data:")
                        print(f"  Asks: {orderbook.get('asks', [])[:5]}")
                        print(f"  Bids: {orderbook.get('bids', [])[:5]}")
                        print(f"  Timestamp: {orderbook.get('timestamp', 'N/A')}")
                        print("---")

                    await self.store.orderbooks.wait()

        except Exception as e:
            logger.error(f"Error in board watcher: {e}")
            raise
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        self.running = False
        if self.client:
            await self.client.close()
            logger.info("GMO Board Watcher stopped")

    async def stop(self) -> None:
        self.running = False


async def main() -> None:
    symbol = os.getenv("GMO_SYMBOL", "BTC_JPY")

    watcher = GMOBoardWatcher(symbol=symbol)

    try:
        await watcher.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        await watcher.cleanup()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
