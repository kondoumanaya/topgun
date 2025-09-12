Exchanges
=========

対応取引所における topgun の個別の仕様について説明。

コード例などについては :doc:`examples` を参照。


bitFlyer
--------

https://lightning.bitflyer.com/docs

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitflyer": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://lightning.bitflyer.com/docs#%E8%AA%8D%E8%A8%BC
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信される (*JSON-RPC 2.0 over WebSocket* のみ) 。

    https://bf-lightning-api.readme.io/docs/realtime-api-auth

WebSocket
~~~~~~~~~

bitFlyer の WebSocket には *Socket.IO* と *JSON-RPC 2.0 over WebSocket* があるが、
topgun の認証と DataStore は *JSON-RPC 2.0 over WebSocket* のみ対応。

DataStore
~~~~~~~~~

* :class:`.bitFlyerDataStore` (*JSON-RPC 2.0 over WebSocket* のみ)

以下の DataStore に格納される値は topgun による独自実装。 また特定のキーのみが更新。
    * :attr:`.bitFlyerDataStore.positions`
        * ``size`` キーのみが更新。
    * :attr:`.bitFlyerDataStore.collateral`
        * ``collateral`` キーのみが更新。
    * :attr:`.bitFlyerDataStore.balance`
        * ``amount`` キーのみが更新。

    .. warning::
        bitFlyer の WebSocket チャンネル ``child_order_events`` は各種データを提供しておらず、計算の元となる約定情報のみを提供。 その為 ``bitFlyerDataStore`` は約定情報から独自に各種データを計算。 値が正確になるよう努めているが、端数処理などの影響で実データとズレが生じる可能性があることに注意。 正確な値を必要とする場合は、HTTP API による :meth:`.bitFlyerDataStore.initialize` を利用。

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


GMO Coin
--------

https://api.coin.z.com/docs/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"gmocoin": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定。

    https://api.coin.z.com/docs/#authentication-private
* WebSocket 認証
    GMO Coin はトークン認証方式。

    https://api.coin.z.com/docs/#authentication-private-ws

    :class:`.helpers.GMOCoinHelper` には「アクセストークン」を管理する機能がある。

    :class:`.helpers.GMOCoinHelper` を利用すると「アクセストークンを延長」と「アクセストークンを取得」を自動で実行。
    さらに取得したアクセストークンから Private WebSocket URL を構築して :attr:`.WebSocketApp.url` を自動で更新。
    通常、 `GMO コインの定期メンテナンス <https://support.coin.z.com/hc/ja/articles/115007815487-%E3%82%B7%E3%82%B9%E3%83%86%E3%83%A0%E3%83%A1%E3%83%B3%E3%83%86%E3%83%8A%E3%83%B3%E3%82%B9%E6%99%82%E9%96%93%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6%E6%95%99%E3%81%88%E3%81%A6%E3%81%8F%E3%81%A0%E3%81%95%E3%81%84>`_
    後はアクセストークンは失効して Private WebSocket の再接続は失敗する。
    このヘルパーを使うと、失効したアクセストークンを自動で再取得するので、メンテナンス後の再接続を確立するのに便利。

    利用可能なコードは :ref:`Examples GMOCoinHelper <GMOCoinHelper>` を参照。

WebSocket
~~~~~~~~~

* レート制限
    topgun は GMO コインの WebSocket API の購読レート制限に対応。

    https://api.coin.z.com/docs/#restrictions

    :meth:`.Client.ws_connect` でメッセージを送信する際、レート制限が自動適用される。

DataStore
~~~~~~~~~

* :class:`.GMOCoinDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


bitbank
-------

https://github.com/bitbankinc/bitbank-api-docs

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitbank": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。 認証方式は ``ACCESS-TIME-WINDOW`` を採用。

    https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api_JP.md#%E8%AA%8D%E8%A8%BC
* PubNub 認証
    :mod:`topgun.helpers.bitbank` のヘルパー関数を利用して、自動的に PubNub の認証を行う。

WebSocket
~~~~~~~~~

* Socket.IO
    bitbank の Public WebSocket は Socket.IO で実装されている。
    topgun は Socket.IO にネイティブでは対応していない為、低レベルで URL の指定と購読リクエストを送信をする必要がある。

    低レベルで Socket.IO の購読リクエストには :meth:`.Client.ws_connect` の引数 ``send_str`` を ``'42["join-room","depth_whole_btc_jpy"]'`` のように指定。

    また topgun は Socket.IO v4 に対応していない。
    接続するには URL で v3 ``EIO=3`` を指定する必要がある。

    利用可能なコードは :doc:`examples` を参照。
* Ping-Pong
    * Socket.IO の Ping-Pong が自動で送信される。

PubNub
~~~~~~

* PubNub クライアント
    bitbank の Private Stream API は PubNub によって配信されている。 これは WebSocket のようなプロトコルではない。

    topgun はヘルパー関数として組み込みの PubNub クライアント :mod:`topgun.helpers.bitbank` を提供。
    このヘルパー関数群では Private Stream API のサブスクライブが可能。 さらにトークンの自動取得・トークンの自動更新を行う。
    また :class:`.bitbankPrivateDataStore` を簡単に利用することが可能。 (:ref:`Examples <bitbankhelper>`)

    別途、ファースト・パーティの `PubNub SDK <https://www.pubnub.com/docs/sdks/python>`_ を利用することも可能 これより高機能 が、ただし topgun の HTTP セッションとは互換性がない。 組み込みのヘルパー関数を利用することで、イベントループをより適切に管理することが可能。

DataStore
~~~~~~~~~

* :class:`.bitbankDataStore`
* :class:`.bitbankPrivateDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


Coincheck
---------

https://coincheck.com/ja/documents/exchange/api

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"coincheck": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://coincheck.com/ja/documents/exchange/api#auth
* WebSocket 認証
    *現時点で Private WebSocket API はない。*

DataStore
~~~~~~~~~

* :class:`.CoincheckDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


OKJ
---

https://dev.okcoin.jp/en/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"okj": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://dev.okcoin.jp/en/#summary-yan-zheng
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信。

    https://dev.okcoin.jp/en/#spot_ws-login

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信。

    https://dev.okcoin.jp/en/#spot_ws-limit

DataStore
~~~~~~~~~

未サポート。


BitTrade
--------

https://api-doc.bittrade.co.jp/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bittrade": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://api-doc.bittrade.co.jp/#4adc7a21f5
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信される。

    https://api-doc.bittrade.co.jp/#7a52d716ff

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信される。

    * https://api-doc.bittrade.co.jp/#401564b16d
    * https://api-doc.bittrade.co.jp/#111d6cb2aa

DataStore
~~~~~~~~~

未サポート。


Bybit
-----

https://bybit-exchange.github.io/docs/v5/intro

V5 API のみ対応している。 V3 API には対応していない。

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bybit": ["API_KEY", "API_SERCRET"]}``
    * ``{"bybit_demo": ["API_KEY", "API_SERCRET"]}``
    * ``{"bybit_testnet": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://bybit-exchange.github.io/docs/v5/guide#authentication
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信される。

    https://bybit-exchange.github.io/docs/v5/ws/connect#authentication

    また Websocket Trade API におけるメッセージ送信では ``header`` オブジェクトにタイムスタンプ ``X-BAPI-TIMESTAMP`` が自動付与される。

    https://bybit-exchange.github.io/docs/v5/websocket/trade/guideline

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信される。

    https://bybit-exchange.github.io/docs/v5/ws/connect#how-to-send-the-heartbeat-packet

DataStore
~~~~~~~~~

* :class:`.BybitDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


Binance
-------

https://developers.binance.com/docs/binance-spot-api-docs/CHANGELOG

topgun は Binance API において Spot /USDⓈ-M / COIN-M / WebSocket API (Spot) で動作確認をしている。

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"binance": ["API_KEY", "API_SERCRET"]}`` (Mainnet: Spot/USDⓈ-M/COIN-M)
    * ``{"binancespot_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet: Spot)
    * ``{"binancefuture_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet: USDⓈ-M/COIN-M)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    * https://developers.binance.com/docs/binance-spot-api-docs/rest-api#signed-endpoint-examples-for-post-apiv3order
    * https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info#signed-trade-and-user_data-endpoint-security
    * https://developers.binance.com/docs/derivatives/coin-margined-futures/general-info#signed-trade-and-user_data-endpoint-security
* WebSocket 認証
    Binance はトークン認証方式の為、ユーザーコードで URL に ``listenKey`` 含める必要がある。

    * https://developers.binance.com/docs/binance-spot-api-docs/user-data-stream
    * https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams/Connect
    * https://developers.binance.com/docs/derivatives/coin-margined-futures/user-data-streams/Connect

    ただし Binance 系 DataStore に ``listenKey`` を管理する機能がある。

    Binance 系 DataStore の ``initialize()`` は「*Create a ListenKey*」系の POST リクエストに対応している。
    これにより ``listenKey`` が DataStore の属性 ``listenkey`` に格納される。
    この属性を利用すると ``listenKey`` 付き URL を構築するのに便利。

    また DataStore 側で「*Ping/Keep-alive a ListenKey*」系の定期リクエストが有効になる為、ユーザーコードでの延長処理は不要。
* WebSocket 認証 (*WebSocket API*)
    topgun では Binance で *WebSocket API* と表されるタイプの API 認証が可能。
    これは WebSocket メッセージで注文の作成などを可能にするもので、現時点では Spot のみ対応している。

    https://developers.binance.com/docs/binance-spot-api-docs/web-socket-api

    送信する WebSocket メッセージに対して、取引所が定める認証情報が自動設定される。

    https://developers.binance.com/docs/binance-spot-api-docs/web-socket-api#signed-trade-and-user_data-request-security

    これを利用するには、 :attr:`.WebSocketApp.current_ws` から ``send_json()`` メソッドを利用して引数 ``auth=topgun.Auth`` を設定する。

WebSocket
~~~~~~~~~

* レート制限
    topgun は Binance Spot のみにある WebSocket API の購読レート制限に対応している。

    https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#websocket-limits

    :meth:`.Client.ws_connect` でメッセージを送信する際、レート制限が自動適用される。


DataStore
~~~~~~~~~

* :class:`.BinanceSpotDataStore` (Spot)
* :class:`.BinanceUSDSMDataStore` (USDⓈ-M)
* :class:`.BinanceCOINMDataStore` (COIN-M)

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


OKX
---

https://www.okx.com/docs-v5/en/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"okx": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}`` (Live trading)
    * ``{"okx_demo": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}`` (Demo trading)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://www.okx.com/docs-v5/en/#overview-rest-authentication
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信される。

    https://www.okx.com/docs-v5/en/#overview-websocket-login

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信される。

    https://www.okx.com/docs-v5/en/#overview-websocket-overview

DataStore
~~~~~~~~~

* :class:`.OKXDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


Phemex
------

https://phemex-docs.github.io/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"phemex": ["API_KEY", "API_SERCRET"]}`` (Mainnet)
    * ``{"phemex_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://phemex-docs.github.io/#rest-request-header
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信される。

    https://phemex-docs.github.io/#user-authentication

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信される。

    https://phemex-docs.github.io/#heartbeat

DataStore
~~~~~~~~~

* :class:`.PhemexDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


Bitget
------

https://www.bitget.com/api-doc/common/intro

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitget": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://www.bitget.com/api-doc/common/signature
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報の WebSocket メッセージが自動送信される。

    https://www.bitget.com/api-doc/common/websocket-intro

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信される。

    https://www.bitget.com/api-doc/common/websocket-intro#connect

DataStore
~~~~~~~~~

* :class:`.BitgetV2DataStore`
* :class:`.BitgetDataStore`


MEXC
----

https://mexcdevelop.github.io/apidocs/spot_v3_en/

.. warning::

    MEXC Future は注文系 API が *maintenance* となっているので、**実質的に API トレードできない**。

    https://mexcdevelop.github.io/apidocs/contract_v1_en/#update-log

    また Spot についても一部銘柄 (**なんと BTC/USDT を含む**) は同じく注文系 API が利用停止になっている。

    `https://support.mexc.com/hc/ja/articles/15149585234969-MEXC-BTC-USDT-FTM-USDT-OP-USDT-DOGE-USDT各取引ペアのAPIアップグレード-及びメンテナンスに関するお知らせ <https://support.mexc.com/hc/ja/articles/15149585234969-MEXC-BTC-USDT-FTM-USDT-OP-USDT-DOGE-USDT%E5%90%84%E5%8F%96%E5%BC%95%E3%83%9A%E3%82%A2%E3%81%AEAPI%E3%82%A2%E3%83%83%E3%83%97%E3%82%B0%E3%83%AC%E3%83%BC%E3%83%89-%E5%8F%8A%E3%81%B3%E3%83%A1%E3%83%B3%E3%83%86%E3%83%8A%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E3%81%8A%E7%9F%A5%E3%82%89%E3%81%9B>`_

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"mexc": ["API_KEY", "API_SERCRET"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://mexcdevelop.github.io/apidocs/spot_v3_en/#signed
* WebSocket 認証
    MEXC はトークン認証方式の為、ユーザーコードで URL に ``listenKey`` 含める必要がある。

    https://mexcdevelop.github.io/apidocs/spot_v3_en/#websocket-user-data-streams

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信される。

    https://mexcdevelop.github.io/apidocs/spot_v3_en/#websocket-market-streams

DataStore
~~~~~~~~~

注文系 API が利用できないことを鑑みて、サポート対象外としている。


KuCoin
------

https://www.kucoin.com/docs/beginners/introduction

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"kucoin": ["API_KEY", "API_SERCRET", "API_PASSPHRASE"]}``
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://www.kucoin.com/docs/basic-info/connection-method/authentication/creating-a-request
* WebSocket 認証
    KuCoin はトークン認証方式の為、ユーザーコードで URL と ``token`` の発行をする必要がある。

    https://www.kucoin.com/docs/websocket/basic-info/apply-connect-token/private-channels-authentication-request-required-

    ただし KuCoin 系 DataStore には発行された URL と ``token`` を管理する機能がある。

    KuCoin 系 DataStore の ``initialize()`` は上記 ``/api/v1/bullet-private`` の POST リクエストに対応している。
    これにより発行された URL と ``token`` が DataStore の属性 ``endpoint`` に格納される。
    この属性を利用すると KuCoin の WebSocket URL を構築するのに便利。

    また同様に ``initialize()`` は ``/api/v1/bullet-public`` の POST リクエストにも対応している。
    https://www.kucoin.com/docs/websocket/basic-info/apply-connect-token/public-token-no-authentication-required-

WebSocket
~~~~~~~~~

* Ping-Pong
    取引所が定める Ping-Pong メッセージが自動送信される。

    https://www.kucoin.com/docs/websocket/basic-info/ping

DataStore
~~~~~~~~~

* :class:`.KuCoinDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。


BitMEX
------

https://www.bitmex.com/app/apiOverview

.. warning::

    BitMEX Mainnet は日本国内からは利出来ない。
    Testnet のみ利用可能。

    https://blog.bitmex.com/ja-jp-notice-to-japan-residents/

Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"bitmex": ["API_KEY", "API_SERCRET"]}`` (Mainnet)
    * ``{"bitmex_testnet": ["API_KEY", "API_SERCRET"]}`` (Testnet)
* HTTP 認証
    HTTP リクエスト時に取引所が定める認証情報が自動設定される。

    https://www.bitmex.com/app/apiKeysUsage#Authenticating-with-an-API-Key
* WebSocket 認証
    WebSocket 接続時に取引所が定める認証情報が自動設定される。

    https://www.bitmex.com/app/wsAPI#API-Keys

DataStore
~~~~~~~~~

* :class:`.BitMEXDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。

Hyperliquid
-----------

https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api


Authentication
~~~~~~~~~~~~~~

* API 認証情報
    * ``{"hyperliquid": ["PRIVATE_KEY"]}`` (Mainnet)
    * ``{"hyperliquid_testnet": ["PRIVATE_KEY"]}`` (Testnet)
* HTTP 認証
    `Exchange endpoint <https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint>`_ (``/exchange``) へのリクエストに対して以下の Request Body を省略することができる。 省略した場合、以下の値が自動設定される。

    * ``nonce``: 現在時刻のミリ秒
    * ``signature``: ``action`` をハッシュ化し秘密鍵で署名した値

    実際の利用方法は :ref:`Examples <examples-place-order-hyperliquid>` を参照。
* WebSocket 認証
    まだ対応していません (Work in progress)。 以下のように手動で署名を行うことも可能。

手動で署名をする必要がある場合は、より低レベルな署名ヘルパー :mod:`topgun.helpers.hyperliquid` を利用。


DataStore
~~~~~~~~~

* :class:`.HyperliquidDataStore`

対応している WebSocket チャンネルはリファレンスの *ATTRIBUTES* を参照。

.. warning::

    部分的なサポート。 一部のチャンネルは未対応。 `#354 <https://github.com/topgun/topgun/issues/354>`_
