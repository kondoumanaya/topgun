[![CI](https://github.com/your-username/your-repo/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/ci.yml)

<!-- 使用ツール（ruffなど） -->

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# topgun

![topgun logo](https://raw.githubusercontent.com/topgun/topgun/main/docs/logo_150.png)

Python botters向けの高度なAPIクライアント。このプロジェクトは日本語対応です。

## 📌 概要

`topgun`は[仮想通貨 botter (crypto bot traders)](https://medium.com/perpdex/botter-the-crypto-bot-trader-in-japan-2f5f2a65856f)向けのPythonライブラリです。

このライブラリは**HTTPおよびWebSocket APIクライアント**です。
取引ボットの開発に役立つ以下の機能を備えています。

## 🚀 機能

- ✨ HTTP / WebSocket クライアント
  - プライベートAPIの**自動認証**
  - WebSocketの**自動再接続**と**自動ハートビート**
  - [`aiohttp`](https://docs.aiohttp.org/)ベースのクライアント
- ✨ DataStore
  - WebSocketメッセージデータハンドラー
  - 板情報更新などの**差分データ処理**
  - **高速データ処理**とクエリ
- ✨ その他の機能
  - 型ヒントのサポート
  - [`asyncio`](https://docs.python.org/ja/3/library/asyncio.html)を使用した非同期プログラミング
  - Discordコミュニティ

## 🏦 対応取引所

| 取引所名     | API認証  | DataStore  | 取引所API文書                                                               |
| ----------- | -------- | ---------- | --------------------------------------------------------------------------- |
| bitFlyer    | ✅       | ✅         | [Link](https://lightning.bitflyer.com/docs)                                 |
| GMO Coin    | ✅       | ✅         | [Link](https://api.coin.z.com/docs/)                                        |
| bitbank     | ✅       | ✅         | [Link](https://github.com/bitbankinc/bitbank-api-docs)                      |
| Coincheck   | ✅       | ✅         | [Link](https://coincheck.com/ja/documents/exchange/api)                     |
| OKJ         | ✅       | 未対応     | [Link](https://dev.okcoin.jp/en/)                                           |
| BitTrade    | ✅       | 未対応     | [Link](https://api-doc.bittrade.co.jp/)                                     |
| Bybit       | ✅       | ✅         | [Link](https://bybit-exchange.github.io/docs/v5/intro)                      |
| Binance     | ✅       | ✅         | [Link](https://developers.binance.com/docs/binance-spot-api-docs/CHANGELOG) |
| OKX         | ✅       | ✅         | [Link](https://www.okx.com/docs-v5/en/)                                     |
| Phemex      | ✅       | ✅         | [Link](https://phemex-docs.github.io/)                                      |
| Bitget      | ✅       | ✅         | [Link](https://www.bitget.com/api-doc/common/intro)                         |
| MEXC        | ✅       | 未対応     | [Link](https://mexcdevelop.github.io/apidocs/spot_v3_en/)                   |
| KuCoin      | ✅       | ✅         | [Link](https://www.kucoin.com/docs/beginners/introduction)                  |
| BitMEX      | ✅       | ✅         | [Link](https://www.bitmex.com/app/apiOverview)                              |
| Hyperliquid | ✅       | 部分対応   | [Link](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api)  |

## 🐍 必要環境

Python 3.9+

## 🔧 インストール

[PyPI](https://pypi.org/project/topgun/)から（安定版）:

```sh
pip install topgun
```

[GitHub](https://github.com/topgun/topgun)から（最新版）:

```sh
pip install git+https://github.com/topgun/topgun.git
```

## ⚠️ 互換性に関する注意

topgunは完全に新しいコードベースv2を計画しています。依存関係として指定する際は、2.0未満のバージョン（`topgun<2.0`）を指定することを推奨します。

> [!IMPORTANT]
> ロードマップはこちら: [topgun/topgun#248](https://github.com/topgun/topgun/issues/248)

## 📝 使用方法

bitFlyer APIの例:

### HTTP API

バージョン1.0からの新しいインターフェース: **Fetch API**。

よりシンプルなリクエスト/レスポンス。

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
        # 残高を取得
        r = await client.fetch("GET", "/v1/me/getbalance")

        print(r.response.status, r.response.reason, r.response.url)
        print(r.data)

        # 注文を作成
        CREATE_ORDER = False  # 注文を作成する場合は`True`に設定
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

aiohttpベースのAPI。

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
        # 残高を取得
        async with client.get("/v1/me/getbalance") as resp:
            data = await resp.json()

        print(resp.status, resp.reason)
        print(data)

        # 注文を作成
        CREATE_ORDER = False  # 注文を作成する場合は`True`に設定
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
        # キューを作成
        wsqueue = topgun.WebSocketQueue()

        # WebSocketに接続してTickerを購読
        await client.ws_connect(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            send_json={
                "method": "subscribe",
                "params": {"channel": "lightning_ticker_BTC_JPY"},
            },
            hdlr_json=wsqueue.onmessage,
        )

        # メッセージを反復処理（Ctrl+Cで中断）
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
        # DataStoreを作成
        store = topgun.bitFlyerDataStore()

        # WebSocketに接続して板情報を購読
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

        # 板情報の最良価格を監視（Ctrl+Cで中断）
        with store.board.watch() as stream:
            async for change in stream:
                board = store.board.sorted(limit=2)
                print(board)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
```

## 📖 ドキュメント

🔗 https://topgun.readthedocs.io/ja/stable/ (日本語)
