[![CI](https://github.com/your-username/your-repo/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/ci.yml)

<!-- 使用ツール（ruffなど） -->

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# topgun

![topgun logo](https://raw.githubusercontent.com/topgun/topgun/main/docs/logo_150.png)

An advanced API client for python botters. This project is in Japanese.

## 📌 Description

`topgun` is a Python library for [仮想通貨 botter (crypto bot traders)](https://medium.com/perpdex/botter-the-crypto-bot-trader-in-japan-2f5f2a65856f).

This library is an **HTTP and WebSocket API client**.
It has the following features, making it useful for developing a trading bot.

## 🚀 Features

- ✨ HTTP / WebSocket Client
  - **Automatic authentication** for private APIs.
  - WebSocket **automatic reconnection** and **automatic heartbeat**.
  - A client based on [`aiohttp`](https://docs.aiohttp.org/).
- ✨ DataStore
  - WebSocket message data handler.
  - **Processing of differential data** such as order book updates
  - **High-speed data processing** and querying
- ✨ Other Experiences
  - Support for type hints.
  - Asynchronous programming using [`asyncio`](https://docs.python.org/ja/3/library/asyncio.html).
  - Discord community.

## 🏦 Exchanges

| Name        | API auth | DataStore  | Exchange API docs                                                           |
| ----------- | -------- | ---------- | --------------------------------------------------------------------------- |
| bitFlyer    | ✅       | ✅         | [Link](https://lightning.bitflyer.com/docs)                                 |
| GMO Coin    | ✅       | ✅         | [Link](https://api.coin.z.com/docs/)                                        |
| bitbank     | ✅       | ✅         | [Link](https://github.com/bitbankinc/bitbank-api-docs)                      |
| Coincheck   | ✅       | ✅         | [Link](https://coincheck.com/ja/documents/exchange/api)                     |
| OKJ         | ✅       | Not yet    | [Link](https://dev.okcoin.jp/en/)                                           |
| BitTrade    | ✅       | Not yet    | [Link](https://api-doc.bittrade.co.jp/)                                     |
| Bybit       | ✅       | ✅         | [Link](https://bybit-exchange.github.io/docs/v5/intro)                      |
| Binance     | ✅       | ✅         | [Link](https://developers.binance.com/docs/binance-spot-api-docs/CHANGELOG) |
| OKX         | ✅       | ✅         | [Link](https://www.okx.com/docs-v5/en/)                                     |
| Phemex      | ✅       | ✅         | [Link](https://phemex-docs.github.io/)                                      |
| Bitget      | ✅       | ✅         | [Link](https://www.bitget.com/api-doc/common/intro)                         |
| MEXC        | ✅       | No support | [Link](https://mexcdevelop.github.io/apidocs/spot_v3_en/)                   |
| KuCoin      | ✅       | ✅         | [Link](https://www.kucoin.com/docs/beginners/introduction)                  |
| BitMEX      | ✅       | ✅         | [Link](https://www.bitmex.com/app/apiOverview)                              |
| Hyperliquid | ✅       | Partially  | [Link](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api)  |

## 🐍 Requires

Python 3.12+

## 🔧 Installation

```sh
pip install -e topgun
```

From [GitHub](https://github.com/topgun/topgun) (latest version):

```sh
pip install git+https://github.com/topgun/topgun.git
```

> [!IMPORTANT]
> The roadmap is here: [topgun/topgun#248](https://github.com/topgun/topgun/issues/248)

## 📝 Usage

Example of bitFlyer API:

### HTTP API

New interface from version 1.0: **Fetch API**.

More simple request/response.

```py
import asyncio

import topgun

apis = {
    "bitflyer": ["YOUER_BITFLYER_API_KEY", "YOUER_BITFLYER_API_SECRET"],
}


async def main():
    async with topgun.Client(
        apis=apis, base_url="https://api.bitflyer.com"
    ) as client:
        # Fetch balance
        r = await client.fetch("GET", "/v1/me/getbalance")

        print(r.response.status, r.response.reason, r.response.url)
        print(r.data)

        # Create order
        CREATE_ORDER = False  # Set to `True` if you are trying to create an order.
        if CREATE_ORDER:
            r = await client.fetch(
                "POST",
                "/v1/me/sendchildorder",
                data={
                    "product_code": "BTC_JPY",
                    "child_order_type": "MARKET",
                    "side": "BUY",
                    "size": 0.001,
                },
            )

            print(r.response.status, r.response.reason, r.response.url)
            print(r.data)


asyncio.run(main())
```

aiohttp-based API.

```python
import asyncio

import topgun

apis = {
    "bitflyer": ["YOUER_BITFLYER_API_KEY", "YOUER_BITFLYER_API_SECRET"],
}


async def main():
    async with topgun.Client(
        apis=apis, base_url="https://api.bitflyer.com"
    ) as client:
        # Fetch balance
        async with client.get("/v1/me/getbalance") as resp:
            data = await resp.json()

        print(resp.status, resp.reason)
        print(data)

        # Create order
        CREATE_ORDER = False  # Set to `True` if you are trying to create an order.
        if CREATE_ORDER:
            async with client.post(
                "/v1/me/sendchildorder",
                data={
                    "product_code": "BTC_JPY",
                    "child_order_type": "MARKET",
                    "side": "BUY",
                    "size": 0.001,
                },
            ) as resp:
                data = await resp.json()

            print(data)


asyncio.run(main())
```

### WebSocket API

```python
import asyncio

import topgun


async def main():
    async with topgun.Client() as client:
        # Create a Queue
        wsqueue = topgun.WebSocketQueue()

        # Connect to WebSocket and subscribe to Ticker
        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json={
                "method": "subscribe",
                "params": {"channel": "lightning_ticker_BTC_JPY"},
            },
            hdlr_json=wsqueue.onmessage,
        )

        # Iterate message (Ctrl+C to break)
        async for msg in wsqueue:
            print(msg)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
```

### DataStore

```py
import asyncio

import topgun


async def main():
    async with topgun.Client() as client:
        # Create DataStore
        store = topgun.bitFlyerDataStore()

        # Connect to WebSocket and subscribe to Board
        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json=[
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_snapshot_BTC_JPY"},
                },
                {
                    "method": "subscribe",
                    "params": {"channel": "lightning_board_BTC_JPY"},
                },
            ],
            hdlr_json=store.onmessage,
        )

        # Watch for the best prices on Board. (Ctrl+C to break)
        with store.board.watch() as stream:
            async for change in stream:
                board = store.board.sorted(limit=2)
                print(board)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
```

## 📖 Documentation

🔗 https://topgun.readthedocs.io/ja/stable/ (Japanese)
