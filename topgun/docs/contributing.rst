Python
------

topgun は最小要求を **Python 3.9** としている。
Python 3.9 の最新マイナーバージョンをインストールしてコーディングすることを推奨。

Python のインストール方法は多岐にわたる。
`こちらの記事 (python.jp) <https://www.python.jp/install/install.html>`__ を参考にするか、または次に紹介する **uv** を利用。

uv
--

**uv** は Astral によって開発されている非常に高速な Python プロジェクトマネージャー 。

uv は機能の一つとして環境作成時に **目的の Python バージョンを自動でダウンロード** するので基本的なセットアップを省略可能。
当プロジェクトでは作業ごとの uv コマンドを Bash スクリプトとして定義済みなので (``scripts`` 配下) これを利用することで簡単にテストなどを実行可能。

https://docs.astral.sh/uv/

uv は上記公式ドキュメントからインストール。


Git
---

まずは `topgun の GitHub リポジトリ <https://github.com/topgun/topgun>`_ を Fork 。

ローカル環境を利用している場合は Git でコードをチェックアウトする。
Git がローカルにない場合はインストール。

.. code:: sh

    git clone https://github.com/<your-account>/topgun

.. NOTE::
    Codespaces 環境なら既に Git がインストール済みでコードがチェックアウトされているはず  ✨


Dependencies
------------

仮想環境の作成と、プロジェクト及び依存関係をインストールする。

.. code:: sh

    ./scripts/sync


CI
--

コードをリモートブランチにプッシュすると **GitHub Actions** によって定義されている CI が実行される。

CI は **Static analysis** と **Type check** 及び **Test** についてのチェックが実施される。
これらのチェックがエラーになる場合は、コードを修正してから再度プッシュ。
またはローカルでチェックを実施する場合は、以下の手順を参考に。


Static analysis
---------------

当プロジェクトではコード静的解析として **Ruff** を採用している。
上記プロジェクトセットアップ時に依存関係としてインストールされる。

https://docs.astral.sh/ruff/

Format
~~~~~~

フォーマット機能を利用してコードを自動修正可能。

.. code:: bash

    ./scripts/format

Lint
~~~~

静的解析機能を利用してコードの品質をチェック可能。

.. code:: bash

    ./scripts/lint


Type check
----------

当プロジェクトではタイプチェッカーとして **mypy** を採用している。
上記プロジェクトセットアップ時に依存関係としてインストールされる。

https://mypy.readthedocs.io/

型チェックのコマンドは以下の通り 。

.. code:: bash

    ./scripts/typing


Testing
-------

当プロジェクトではテストに **pytest** を採用している。
上記プロジェクトセットアップ時に依存関係としてインストールされる。

https://docs.pytest.org

実装したコードに対するテストコードを作成。
テストコードは ``tests/`` 配下にある。

.. code:: sh

    ./scripts/test

全ての Python バージョンに対してテストカバレッジを実行するには、以下のコマンドを実行。

.. code:: sh

    ./scripts/test-all

テストを実行すると標準出力と HTML のカバレッジレポートが生成される。
HTML のレポートを確認するには、以下のコマンドを実行。

.. code:: sh

    python -m http.server -d htmlcov

**テストの基準**

* すべてのコードに対して **全て** テストを書く。 カバレッジ率は 100%  。
* 例外として :ref:`DataStore <datastore>` に関する単体テストコードは、テスト方法を確立するまで省略している。
* ただし DataStore の動作確認ができる実環境用の機能テストコードを Pull request のコメントに張り付ける。
* 外部との通信部分はモック化。


Documentation
-------------

Sphinx ドキュメントを自動ビルドしてローカル環境で閲覧することが可能。

.. code:: sh

    ./scripts/serve

ローカル環境にホストせずにドキュメントをビルドすることも可能。

.. code:: sh

    ./scripts/docs


Branch Strategy
---------------

GitHub Flow (`日本語訳 <https://gist.github.com/Gab-km/3705015>`_) に従いる。

main ブランチが最新の開発ブランチ 。
Fork 及び Clone したリポジトリの main からトピックブランチ (例: ``fix-some-auth``)を作成する。

.. code:: sh

    git switch -c fix-some-auth main

変更したコードをリモートにプッシュしたら upstream/main を対象に Pull request を送信。


Pull request
------------

Branch Strategy に記したように、main ブランチを対象に Pull request を送信。

Pull request タイトルは、英語でかつコミットメッセージとなる文で記述することを推奨する。
(例: *Fix xxx in SomeExchangeDataStore* *Support SomeExchange HTTP auth* など)
内容については日本語でも構いません。

Pull request はメンテナによって *Squash-and-Merge* 戦略でマージされる。
*Squash-and-Merge* 戦略とは Pull request の変更が複数のコミットあったとしてもマージ時に 1 つに押し潰される。
