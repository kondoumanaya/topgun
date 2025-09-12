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
    async with topgun.Client(base_url="https://coincheck.com") as client:
        store = topgun.CoincheckDataStore()

        await client.ws_connect(
            "wss://ws-api.coincheck.com/",
            send_json={"type": "subscribe", "channel": "btc_jpy-orderbook"},
            hdlr_json=store.onmessage,
        )

        await store.initialize(
            client.get("/api/order_books", params={"pair": "btc_jpy"})
        )

        while True:
            orderbook = store.orderbook.sorted(limit=2)
            print(orderbook)

            await store.orderbook.wait()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
