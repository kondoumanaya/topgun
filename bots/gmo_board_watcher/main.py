#!/usr/bin/env python3
"""
GMO Coin Board Watcher Bot
Simple implementation that outputs board information to stdout
"""

import asyncio
import json
import logging
import os
import sys
from contextlib import suppress
from typing import Any

import aiohttp

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class GMOBoardWatcher:
    """Simple GMO Coin board data watcher using direct WebSocket connection"""

    def __init__(self, symbol: str = "BTC_JPY") -> None:
        self.symbol = symbol
        self.session: aiohttp.ClientSession | None = None
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self.running = False

    async def start(self) -> None:
        """Start watching GMO Coin board data"""
        self.session = aiohttp.ClientSession()

        try:
            self.ws = await self.session.ws_connect(
                "wss://api.coin.z.com/ws/public/v1")

            subscribe_msg = {
                "command": "subscribe",
                "channel": "orderbooks",
                "symbol": self.symbol,
            }
            await self.ws.send_str(json.dumps(subscribe_msg))

            self.running = True
            logger.info(
                f"Started watching GMO Coin board data for {self.symbol}")

            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_message(data)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode message: {msg.data}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.ws.exception()}")
                    break

                if not self.running:
                    break

        except Exception as e:
            logger.error(f"Error in board watcher: {e}")
            raise
        finally:
            await self.cleanup()

    async def _handle_message(self, data: dict[str, Any]) -> None:
        """Handle incoming WebSocket message"""
        if (data.get("channel") == "orderbooks" and
                data.get("symbol") == self.symbol):
            asks = data.get("asks", [])[:5]  # Top 5 asks
            bids = data.get("bids", [])[:5]  # Top 5 bids
            timestamp = data.get("timestamp", "N/A")

            print(f"[{self.symbol}] Board Data:")
            print(f"  Asks: {asks}")
            print(f"  Bids: {bids}")
            print(f"  Timestamp: {timestamp}")
            print("---")

    async def cleanup(self) -> None:
        """Clean up resources"""
        self.running = False
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
        logger.info("GMO Board Watcher stopped")

    async def stop(self) -> None:
        """Stop the watcher"""
        self.running = False


async def main() -> None:
    """Main entry point"""
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
