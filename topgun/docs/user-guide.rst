User Guide
==========

Client class
------------

:class:`topgun.Client` は HTTP リクエストを行う為のメインクラス。
:class:`.Client` の利用を開始するにはいくつかのステップが必要。

1. :mod:`asyncio` と :mod:`topgun` を ``import`` する
2. 非同期関数を *async def* で定義する
3. 定義した非同期関数の中から *async with* ブロックで :class:`.Client` インスタンスを初期化する

.. code:: python

    import asyncio

    import topgun


    async def main():
        async with topgun.Client() as client:
            ...


    asyncio.run(main())

:class:`.Client` インスタンスのメソッドから、以降に説明する HTTP リクエストと WebSocket 接続の機能を利用することができる。

.. note::

    topgun の中核機能は `asyncio <https://docs.python.org/ja/3/library/asyncio.html>`_ と `aiohttp <https://docs.aiohttp.org/en/stable/client_quickstart.html>`__ の上に構築されている。
    それらの知識が全くないと、このユーザーガイドを進めるのは難しい。

    asyncio と aiohttp を掻い摘んで理解するには、こちらの記事がおすすめ。

    botterのためのasyncio
    https://zenn.dev/mtkn1/articles/c61e77c1d221aa

.. note::

    このユーザーガイドの以降で説明する HTTP / WebSocket API には、仮想通貨取引所 bitFlyer の API を例として利用。
    ただし bitFlyer API の詳しい内容は説明を行わない。
    公式ドキュメントを確認。

    https://lightning.bitflyer.com/docs


HTTP API
-------------

.. _fetch-api:

Fetch API
~~~~~~~~~

:meth:`.Client.fetch` メソッドで HTTP リクエストを作成。

:ref:`Fetch API <fetch-api>` は従来の :ref:`HTTP メソッド API <http-method-api>` と比較して、シンプルなリクエスト／レスポンスのフローを提供。
一度の ``await`` 式で HTTP レスポンスデータの JSON デコードまで行う。

.. code-block:: python

    async def main():
        async with topgun.Client() as client:
            result = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(result.response.status, result.response.reason)
            print(result.data)


第 1 引数 (``method``) は HTTP メソッド。 文字列で ``"GET"`` ``"POST"`` 等の HTTP メソッドを指定。
第 2 引数 (``url``) はリクエストの URL 。 文字列で指定。

返り値は :class:`.FetchResult`
:attr:`.FetchResult.response` 属性には `aiohttp.ClientResponse <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse>`_ が格納されており、
:attr:`.FetchResult.data` 属性にはデコードされた JSON データが格納されている。

.. versionadded:: 1.0

.. _http-method-api:

HTTP method API
~~~~~~~~~~~~~~~

従来の :ref:`HTTP メソッド API <http-method-api>` で HTTP リクエストを作成。

:ref:`HTTP メソッド API <http-method-api>` でリクエストを開始するには *async with* ブロックを利用。
こちらは従来の `aiohttp.ClientSession <https://docs.aiohttp.org/en/stable/client_reference.html#client-session>`_ と同様のリクエスト／レスポンスのフローになる。

* :meth:`.Client.request`
* :meth:`.Client.get`
* :meth:`.Client.post`
* :meth:`.Client.put`
* :meth:`.Client.delete`

.. code-block:: python

    async def main():
        async with topgun.Client() as client:
            async with client.request(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            ) as resp:
                data = await resp.json()
            print(data)

            async with client.get(
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            ) as resp:
                data = await resp.json()
            print(data)

まず *async with* ブロックの返り値によってレスポンス `aiohttp.ClientResponse <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse>`_ を受信。
このレスポンスは HTTP ヘッダーまでとなる。
そして *async* :meth:`json` メソッドを ``await`` するによって残りの HTTP 本文が受信され、データが JSON としてデコードされた値が返る。

Request parameters
~~~~~~~~~~~~~~~~~~

HTTP リクエストのパラメーターは ``params`` 引数または ``data`` 引数に指定。

``params`` 引数は「**URL クエリ文字列**」
主に ``GET`` リクエストに利用。
ただし一部の仮想通貨取引所 API においては ``POST PUT DELETE`` リクエストでも利用することがある。

.. code:: python

    async def main():
        async with topgun.Client() as client:
            result = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(r.response.status, r.response.reason)
            print(result.data)

``data`` 引数は「**HTTP 本文**」。
主に ``POST`` リクエストで送信する JSON データとして利用。

.. code:: python

    async def main():
        async with topgun.Client() as client:
            result = await client.fetch(
                "POST",
                "https://api.bitflyer.com/v1/me/sendchildorder",
                data={"product_code": "BTC_JPY", "child_order_type": "MARKET", "size": 0.01},
            )  # NOTE: Authentication is required
            print(r.response.status, r.response.reason)
            print(result.data)

これらの仕様は :ref:`Fetch API <fetch-api>` と :ref:`HTTP メソッド API <http-method-api>` の間でも同様。

.. note::

    この例は bitFlyer の「新規注文を出す」 API 。 実際にこれをリクエストするには自動認証 :ref:`authentication` が必要。

.. warning::

    aiohttp の知識がある方は JSON データの POST リクエストに ``json`` 引数を使おうとするかもしれない。
    **しかし topgun では** ``json`` **引数は利用できない** 。
    これは topgun の自動認証処理による影響。
    対応する取引所では ``data`` 引数を指定すると適切な JSON またはフォームなどの Content-Type が設定される。

Response headers and data
~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`Fetch API <fetch-api>` の戻り値におけるオブジェクト属性 :attr:`.FetchResult.response` と、
:ref:`HTTP メソッド API <http-method-api>` の戻り値は共に `aiohttp.ClientResponse <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientResponse>`_

HTTP レスポンスヘッダーについては、 ``headers`` 属性から取得可能。

.. code:: python

    async def main():
        async with topgun.Client() as client:
            # Fetch API
            r = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(r.response.headers)

            # HTTP method API
            async with client.get(
                "https://api.bitflyer.com/v1/getticker", params={"product_code": "BTC_JPY"}
            ) as resp:
                print(resp.headers)

HTTP レスポンスの JSON データについては、:ref:`Fetch API <fetch-api>` と :ref:`HTTP メソッド API <http-method-api>` にある説明の通り。
:ref:`Fetch API <fetch-api>` では :attr:`.FetchResult.data` に格納されており、 :ref:`HTTP メソッド API <http-method-api>` では *async* :meth:`json` メソッドを ``await`` することで取得できる。

.. code:: python

    async def main():
        async with topgun.Client() as client:
            # Fetch API
            r = await client.fetch(
                "GET",
                "https://api.bitflyer.com/v1/getticker",
                params={"product_code": "BTC_JPY"},
            )
            print(r.data)

            # HTTP method API
            async with client.get(
                "https://api.bitflyer.com/v1/getticker", params={"product_code": "BTC_JPY"}
            ) as resp:
                data = await resp.json()
                print(data)

Base URL
--------

:class:`.Client` の引数 ``base_url`` を設定することで、取引所 API エンドポイントのベース URL を省略して HTTP リクエストができる。

``base_url`` を設定した場合、HTTP リクエストでは続きの相対 URL パスを設定。

.. code:: python

    async def main():
        async with topgun.Client(base_url="https://api.bitflyer.com") as client:
            r = await client.fetch("GET", "/v1/getticker")
            r = await client.fetch("GET", "/v1/getboard")

            await client.ws_connect("wss://ws.lightstream.bitflyer.com/json-rpc")  # Base URL is not applicable

ただし topgun では WebSocket API の URL には ``base_url`` は適用しない。
これは基本的に取引所の HTTP API と WebSocket API のベース URL が異なっている為であり、殆どの場合で期待される動作。


.. _websocket-api:

WebSocket API
-------------

:meth:`.Client.ws_connect` メソッドで WebSocket 接続を作成。

このメソッドは :mod:`asyncio` の機能により非同期で WebSocket コネクションを作成。

.. code-block:: python

    async def main():
        async with topgun.Client() as client:
            ws = await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_ticker_BTC_JPY"},
                },
                hdlr_json=lambda msg, ws: print(msg),
            )
            await ws.wait()  # Ctrl+C to break

* WebSocket メッセージの送信
    ``send_str``, ``send_bytes``, ``send_json`` 引数で送信する WebSocket メッセージを指定。

    これらの引数は送信するメッセージをリストで括ることで複数のメッセージを送信できる (:ref:`multiple-websocket-senders-handlers`) 。
* WebSocket メッセージの受信
    ``hdlr_str``, ``hdlr_bytes``, ``hdlr_json`` 引数で受信した WebSocket メッセージのハンドラ (コールバック) を指定。
    指定するハンドラは第 1 引数 ``msg: aiohttp.WSMessage`` 第 2 引数 ``ws: aiohttp.ClientWebSocketResponse`` を取る必要がある。
    上記のコードでは無名関数をハンドラに指定して WebSocket メッセージを標準出力している。

    topgun には組み込みのハンドラとして、汎用性の高い :ref:`websocketqueue` や、 :ref:`取引所固有の DataStore <exchange-specific-datastore>` がある。

    これらの引数はハンドラをリストで括ることで複数のハンドラを指定できる (:ref:`multiple-websocket-senders-handlers`) 。
* 再接続
    さらに :meth:`.Client.ws_connect` メソッドで作成した WebSocket 接続は **自動再接続** の機能を備えている。 これにより切断を意識することなく継続的にデータの取得が可能。

戻り値は :class:`.WebSocketApp`  。 このクラスを利用して WebSocket のコネクションを操作可能。
上記の例では :meth:`.WebSocketApp.wait` メソッドで WebSocket の終了を待つことでプログラムの終了を防いでいる。

.. note::

    :class:`.WebSocketApp` は自動再接続の機構がある。 その為 :meth:`.WebSocketApp.wait` の待機は **実質的に無限待機** 。
    トレード bot ではなく、データ収集スクリプトなどのユースケースではハンドラに全ての処理を任せる場合がある。
    そうした時に :meth:`.WebSocketApp.wait` はプログラムの終了を防ぐのに役に立つ。


.. _authentication:

Authentication
--------------

仮想通貨取引所の Private API を利用するには、API キー・シークレットによるユーザー認証が必要。

topgun では :class:`.Client` クラスの引数 ``apis`` に API 認証情報を渡すことで、認証処理が自動的に行われる。

以下のコードでは自動認証を利用して bitFlyer の Private API で資産残高の取得 (``/v1/me/getbalance``) のリクエストを作成。

.. code:: python

    async def main():
        apis = {
            "bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"],
        }
        async with topgun.Client(apis=apis) as client:
            result = await client.fetch("GET", "https://api.bitflyer.com/v1/me/getbalance")
            print(result.data)

まるで Public API かのように Private API をリクエストを作成可能

もちろん、WebSocket API でも自動的に認証処理が行われる。
以下のコードでは bitFlyer の Private WebSocket API で注文イベント (``child_order_events``) を購読。

.. code:: python

    async def main():
        apis = {
        "bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"],
        }
        async with topgun.Client(apis=apis) as client:
            ws = await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "child_order_events"},
                    "id": 123,
                },
                hdlr_json=lambda msg, ws: print(msg),
            )
            await ws.wait()  # Ctrl+C to break

.. warning::
    コード上に API 認証情報をハードコードすることはセキュリティリスクがある。
    ドキュメント上は説明の為にハードコードしているが、実際は環境変数を利用して ``os.getenv`` などから取得することを推奨。

引数 ``apis`` の形式は以下のような辞書形式。

.. code-block:: python

    {
        "API_NAME": [
            "YOUR_API_KEY",
            "YOUR_API_SECRET",
            # "API_PASSPHRASE",  # Optional
        ],
        "...": ["...", "..."],
    }

topgun の自動認証が対応している取引所の API 名はこちらの表から設定する。

========================= =========================
Exchange                  API name
========================= =========================
Binance                   ``binance``
Binance Testnet (Future)  ``binancefuture_testnet``
Binance Testnet (Spot)    ``binancespot_testnet``
bitbank                   ``bitbank``
bitFlyer                  ``bitflyer``
Bitget                    ``bitget``
BitMEX                    ``bitmex``
BitMEX Testnet            ``bitmex_testnet``
Bybit                     ``bybit``
Bybit Demo trading        ``bybit_demo``
Bybit Testnet             ``bybit_testnet``
Coincheck                 ``coincheck``
GMO Coin                  ``gmocoin``
Hyperliquid               ``hyperliquid``
Hyperliquid Testnet       ``hyperliquid_testnet``
KuCoin                    ``kucoin``
MECX                      ``mexc``
OKX                       ``okx``
OKX Demo trading          ``okx_demo``
Phemex                    ``phemex``
Phemex Testnet            ``phemex_testnet``
OKJ                       ``okj``
BitTrade                  ``bittrade``
========================= =========================

また ``apis`` 引数に辞書オブジェクトではなく代わりに **JSON ファイルパス** を文字列として渡すことで、topgun はその JSON ファイルを読み込む。

.. code:: python

    async def main():
        async with topgun.Client(apis="/path/to/apis.json") as client:
            ...

さらに :ref:`implicit-loading-of-apis` では、独自の環境変数などを利用して ``apis`` 引数の指定を省略して API 認証情報のハードコードを避けることができる。

.. _datastore:

DataStore
---------

:ref:`datastore` を利用することで WebSocket からのデータを簡単に処理、参照ができる。

:ref:`datastore` は「ドキュメント指向データベース」のような機能とデータ構造を持っている。
以下はデータを参照する為のメソッド :meth:`.DataStore.get` と :meth:`.DataStore.find` の利用例。

>>> ds = topgun.DataStore(
...     keys=["id"],
...     data=[
...         {"id": 1, "data": "foo"},
...         {"id": 2, "data": "bar"},
...         {"id": 3, "data": "baz"},
...         {"id": 4, "data": "foo"},
...     ],
... )
>>> print(ds.get({"id": 1}))
{'id': 1, 'data': 'foo'}
>>> print(ds.get({"id": 999}))
None
>>> print(ds.find())
[{'id': 1, 'data': 'foo'}, {'id': 2, 'data': 'bar'}, {'id': 3, 'data': 'baz'}, {'id': 4, 'data': 'foo'}]
>>> print(ds.find({"data": "foo"}))
[{'id': 1, 'data': 'foo'}, {'id': 4, 'data': 'foo'}]
>>> print(ds.find({"id": "SPAM"}))
[]

* :meth:`.DataStore.get`
    * DataStore のキーを指定して一意のアイテム (1 件の辞書) を取得
    * 一致するアイテムがない場合 ``None`` が返される
* :meth:`.DataStore.find`
    * アイテムをリストで取得する
    * クエリを指定しない場合全てのデータを取得される
    * クエリを指定すると条件のデータのみを取得する。 一致するアイテムがない場合は空のリストが返される

ただし基本的に **DataStore クラスをそのまま利用するケースはない**。

上記の例では :meth:`.DataStore.get` と :meth:`.DataStore.find` の説明の為に DataStore をそのまま利用。
基本的なユースケースでは次の :ref:`取引所固有の DataStore <exchange-specific-datastore>` を利用。
そこで格納されたデータを参照する方法として上記のメソッドを覚えておく必要がある。

.. note::
    DataStore は、仮想通貨取引所の WebSocket API から高頻度で配信されるリアルタイムデータを処理してトレード bot から利用できるようにする為に開発された。

    DataStore の設計は MongoDB などの「ドキュメント指向データベース」を参考にしており、それを単純なリストと辞書のデータ構造で実現している。
    :mod:`sqlite3` のインメモリ機能などと比べても高速なデータ参照を実現している。

    またキー情報をハッシュ化してインデックスを作成することで一意のデータを特定できるようにしている。
    それにより非常に高い頻度で更新される板情報などの更新処理に対応している。
    例えば Pandas DataFrame などのリッチなデータライブラリでリアルタイムの板情報を扱おうとすると、処理時間の注意が必要。
    DataFrame の更新には多くの処理が含まれる為、配信されるデータの更新頻度に対して DataFrame の更新処理が追い付かない場合がある。
    それに比べて topgun の DataStore はシンプルなデータを構造により高速な更新処理を実現している。

    ただし DataStore の内部構造は説明のように単純なリストと辞書なので **破壊可能である** ことに注意が必要。
    取得したアイテムをユーザー側で更新するべきではない。


.. _exchange-specific-datastore:

Exchange-specific DataStore
---------------------------

:ref:`取引所固有の DataStore <exchange-specific-datastore>` は対応取引所における WebSocket チャンネルの DataStore 実装。

つまり、購読した WebSocket チャンネルのデータがこの取引所固有の DataStore に解釈されることでデータを利用できるようになる。

それぞれの :ref:`取引所固有の DataStore <exchange-specific-datastore>` は :class:`.DataStoreCollection` を継承しており、これは :class:`.DataStore` の集まり。
:class:`.DataStoreCollection` と :class:`.DataStore` の関係を一般的な RDB システムに例えると
「データベース」と「テーブル」のようなもの。 「データベース」には複数の「テーブル」が存在しており、「テーブル」にはデータの実体がある。

例:

* :class:`.bitFlyerDataStore` (bitFlyer の WebSocket データをハンドリングする :class:`.DataStoreCollection`)
    * :attr:`.bitFlyerDataStore.ticker` (bitFlyer の Ticker チャンネルをハンドリングする :class:`.DataStore`)
    * :attr:`.bitFlyerDataStore.executions` (bitFlyer の約定履歴チャンネルをハンドリングする :class:`.DataStore`)
    * :attr:`.bitFlyerDataStore.board` (bitFlyer の板情報チャンネルをハンドリングする :class:`.DataStore`)
    * ...

topgun で提供されている取引所固有の DataStore は :doc:`exchanges` のページから探せる。
全てのリファレンスについては :ref:`exchange-specific-datastore-reference` のページにある。

Attributes
~~~~~~~~~~

WebSocket チャンネルに対応する DataStore は、それぞれの取引所固有の DataStore の属性として割り当てられている。

>>> store = topgun.bitFlyerDataStore()
>>> store.ticker
<topgun.models.bitflyer.Ticker object at 0x7f766b9d67f0>
>>> store.executions
<topgun.models.bitflyer.Executions object at 0x7f766b9d6730>
>>> store.board
<topgun.models.bitflyer.Board object at 0x7f7666398d90>

WebSocket チャンネルに対応する全ての属性については、個別のリファレンスを参照。

.. _onmessage:

onmessage
~~~~~~~~~

取引所固有の DataStore を利用するには、コールバック :attr:`.DataStoreCollection.onmessage` を :meth:`.Client.ws_connect` のハンドラ引数に渡す。

次のコードは bitFlyer の Ticker チャンネルを購読して DataStore としてデータを参照する例。

.. code:: python

    async def main():
        async with topgun.Client() as client:
            store = topgun.bitFlyerDataStore()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_ticker_BTC_JPY"},
                    "id": 1,
                },
                hdlr_json=store.onmessage,
            )

            while True:  # Ctrl+C to break
                ticker = store.ticker.get({"product_code": "BTC_JPY"})
                print(ticker)

                await store.ticker.wait()

.. _initialize:

initialize
~~~~~~~~~~

WebSocket API は HTTP API と違って購読を開始しても「それ以降に更新されたデータ」しか配信されない場合がある。
そうするとプログラム開始時に「初期データ」が存在せず DataStore は空になってしまうので、トレード bot で利用するには不便。

*async* :meth:`.DataStoreCollection.initialize` メソッドを利用すると HTTP API のデータを初期データとして格納できる。

次のコードは bitFlyer のポジションを HTTP API で初期化して、約定イベントチャンネルを購読することで完全なポジションを構築する例。

.. code:: python

    async def main():
        apis = {
        "bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"],
        }
        async with topgun.Client(apis=apis, base_url="https://api.bitflyer.com") as client:
            store = topgun.bitFlyerDataStore()

            await store.initialize(
                client.get("/v1/me/getpositions", params={"product_code": "FX_BTC_JPY"})
            )

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json=[
                    {
                        "method": "subscribe",
                        "params": {"channel": "child_order_events"},
                        "id": 1,
                    },
                ],
                hdlr_json=store.onmessage,
            )

            while True:  # Ctrl+C to break
                positions = store.positions.find()
                print(positions)

                await store.positions.wait()

:meth:`.DataStoreCollection.initialize` はそれぞれの取引所固有の DataStore において個別に実装されている。
その為、初期化に対応している HTTP API エンドポイントも異なる。
詳しくは個別のリファレンスを参照。

.. _sorted:

sorted
~~~~~~

取引所固有の DataStore において Order Book 系の DataStore には :meth:`.DataStore.sorted` メソッドが実装されている。

これを利用するとリストでデータを参照する :meth:`.DataStore.find` とは違って、 ``{"asks": [...], "bids": [...]}`` のような辞書形式で板情報が参照可能。
また板情報はソート済みで返されるのでトレード bot で利用するのに便利。

次のコードは bitFlyer の板情報を :meth:`.DataStore.sorted` で取得する例。

.. code:: python

    async def main():
        async with topgun.Client() as client:
            store = topgun.bitFlyerDataStore()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json=[
                    {
                        "method": "subscribe",
                        "params": {"channel": "lightning_board_snapshot_BTC_JPY"},
                        "id": 1,
                    },
                    {
                        "method": "subscribe",
                        "params": {"channel": "lightning_board_BTC_JPY"},
                        "id": 2,
                    },
                ],
                hdlr_json=store.onmessage,
            )

            while True:  # Ctrl+C to break
                board = store.board.sorted(limit=2)
                print(board)

                await store.board.wait()

.. _wait:

wait
~~~~

*async* :meth:`.DataStore.wait` メソッドは、その DataStore に更新が発生するまで待機できる。

上で説明した :ref:`onmessage` と :ref:`sorted` の例では、データの受信が始まる前に ``while True`` のループが始まるので最初に ``None`` や空のデータが標準出力されるはず。
DataStore の参照をする前に :meth:`.DataStore.wait` することでデータの受信を待機できる。

次のコードは bitFlyer の Ticker を 2 銘柄を購読して受信するまで待機する例。

.. code:: python

    async def main():
        async with topgun.Client() as client:
            store = topgun.bitFlyerDataStore()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json=[
                    {
                        "method": "subscribe",
                        "params": {"channel": "lightning_ticker_BTC_JPY"},
                        "id": 1,
                    },
                    {
                        "method": "subscribe",
                        "params": {"channel": "lightning_ticker_ETH_JPY"},
                        "id": 2,
                    },
                ],
                hdlr_json=store.onmessage,
            )

            while not len(store.ticker):
                await store.ticker.wait()

            print(store.ticker.find())

.. _watch:

watch
~~~~~

*async* :meth:`.DataStore.watch` メソッドは、変更ストリームを開いて ``async for`` ループで更新データを待機及び取得できる。

*async* :meth:`.DataStore.wait` メソッドと同様に待機できるが、:meth:`.DataStore.watch` では変更データとその詳細を取得できる。

次のコードは bitFlyer の約定履歴を :meth:`.DataStore.watch` で監視する例。

.. code:: python

    async def main():
        async with topgun.Client() as client:
            store = topgun.bitFlyerDataStore()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_executions_BTC_JPY"},
                    "id": 1,
                },
                hdlr_json=store.onmessage,
            )

            with store.executions.watch() as stream:
                async for change in stream:  # Ctrl+C to break
                    print(change.data)

.. _websocketqueue:

WebSocketQueue
--------------

DataStore が実装されていない取引所であったり、自らの実装でデータを処理したい場合は :class:`.WebSocketQueue` を利用できる。

.. code-block:: python

    async def main():
        async with topgun.Client() as client:
            wsqueue = topgun.WebSocketQueue()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_ticker_BTC_JPY"},
                },
                hdlr_json=wsqueue.onmessage,
            )

            async for msg in wsqueue:  # Ctrl+C to break
                print(msg)


Differences with aiohttp
------------------------

aiohttp との違いについて。

topgun は `aiohttp <https://pypi.org/project/aiohttp/>`__ を基盤として利用しているライブラリ。

その為、:class:`topgun.Client` におけるインターフェースの多くは ``aiohttp.ClientSession`` と同様。
また topgun の HTTP リクエストのレスポンスクラスは aiohttp のレスポンスクラスを返す。
その為 topgun を高度に利用するには aiohttp ライブラリについても理解しておくことが重要。

ただし **重要な幾つかの違いも存在する** 。

* topgun は HTTP リクエストの自動認証機能により、自動的に HTTP ヘッダーなどを編集。
* topgun では POST リクエストなどのデータは引数 ``data`` に渡する。 aiohttp では ``json`` 引数を許可するが topgun では許可されない。 これは認証機能による都合。
* :meth:`topgun.Client.fetch` は topgun 独自の API  。 aiohttp には存在しません。
* :meth:`topgun.Client.ws_connect` は aiohttp にも存在するが、 topgun では全く異なる独自の API になっている。 これは再接続機能や認証機能を搭載する為。
