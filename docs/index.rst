.. topgun documentation master file, created by
    sphinx-quickstart on Thu Aug  5 19:33:41 2021.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

topgun
=========

.. toctree::
    :maxdepth: 2
    :hidden:

    user-guide
    advanced
    exchanges
    examples
    reference
    contributing

**topgun** は仮想通貨取引所向けの **非同期 HTTP / WebSocket API クライアント**  。

様々な取引所の Private API 認証に対応しており、素早くトレード bot を構築することが可能。
また **WebSocket** と **DataStore** の機能を使うことで、リアルタイムデータを簡単に利用可能。


Installation
------------



⚠️ Compatibility warning
------------------------

topgun は現在次期バージョン (**v2**) を計画している。 v2 ではコードベースのゼロから作り直され、全く新しい仕様に変更される予定 。 そのため、v1 で作成されたプログラムは v2 に対応していません。

``requirements.txt`` や ``pyproject.toml`` などで topgun を依存関係として指定している場合、 **バージョン指定** を行うことをお勧めする。 例えば、 ``topgun<2.0`` と指定することで、v2 がリリースされても自動的にアップデートされないようにすることが可能。

プロジェクト管理ツール (Poetry, PDM, Rye, UV など) を使っている場合は例として以下のようにバージョン指定をする:

.. code-block:: console

    $ poetry|pdm|rye|uv add 'topgun<2.0'

.. important::
    topgun v2 のロードマップはこちらにある！ `topgun/topgun#248 <https://github.com/topgun/topgun/issues/248>`_


Quickstart
----------

`bitFlyer <https://lightning.bitflyer.com/trade>`_ の Private HTTP API と WebSocket API を利用する例 。

* HTTP API (Get Balance):

.. code-block:: python

    import asyncio

    import topgun


    async def main():
        apis = {"bitflyer": ["BITFLYER_API_KEY", "BITFLYER_API_SECRET"]}

        async with topgun.Client(
            apis=apis, base_url="https://api.bitflyer.com"
        ) as client:
            r = await client.fetch("GET", "/v1/me/getbalance")

            print(r.data)


    if __name__ == "__main__":
        asyncio.run(main())

.. note::
    :class:`topgun.Client` に API 認証情報 ``apis`` を入力することで、HTTP リクエストの **自動認証機能** が有効になる。

* WebSocket API (Ticker channel):

.. code-block:: python

    import asyncio

    import topgun


    async def main():
        async with topgun.Client() as client:
            wsqueue = topgun.WebSocketQueue()

            await client.ws_connect(
                "wss://ws.lightstream.bitflyer.com/json-rpc",
                send_json={
                    "method": "subscribe",
                    "params": {"channel": "lightning_ticker_BTC_JPY"},
                    "id": 1,
                },
                hdlr_json=wsqueue.onmessage,
            )

            async for msg in wsqueue:  # Ctrl+C to break
                print(msg)


    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass

.. note::
    :meth:`topgun.Client.ws_connect` により、自動再接続機構を備えた WebSocket コネクションが作成される。

.. warning::
    WebSocket メッセージの受信は永続的に実行される。 プログラムを終了するには ``Ctrl+C`` を入力する。


What's next
-----------

まずは :doc:`user-guide` ページで topgun の利用方法を学習。


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
