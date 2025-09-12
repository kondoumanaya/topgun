# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "topgun",
#     "rich",
# ]
# ///

import asyncio
from contextlib import suppress

import topgun

with suppress(ImportError):
    from rich import print


async def main():
    async with topgun.Client() as client:
        store = topgun.BybitDataStore()

        await client.ws_connect(
            "wss://stream.bybit.com/v5/public/linear",
            send_json={"op": "subscribe", "args": ["orderbook.50.BTCUSDT"]},
            hdlr_json=store.onmessage,
        )

        while True:
            orderbook = store.orderbook.sorted(limit=2)
            print(orderbook)

            await store.orderbook.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
