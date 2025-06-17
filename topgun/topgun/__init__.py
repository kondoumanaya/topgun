from __future__ import annotations

from topgun.__version__ import __version__
from topgun.auth import Auth
from topgun.client import Client, FetchResult, NotJSONContent
from topgun.models.binance import (
    BinanceCOINMDataStore,
    BinanceSpotDataStore,
    BinanceUSDSMDataStore,
)
from topgun.models.bitbank import bitbankDataStore, bitbankPrivateDataStore
from topgun.models.bitflyer import bitFlyerDataStore
from topgun.models.bitget import BitgetDataStore
from topgun.models.bitget_v2 import BitgetV2DataStore
from topgun.models.bitmex import BitMEXDataStore
from topgun.models.bybit import BybitDataStore
from topgun.models.coincheck import CoincheckDataStore
from topgun.models.gmocoin import GMOCoinDataStore
from topgun.models.hyperliquid import HyperliquidDataStore
from topgun.models.kucoin import KuCoinDataStore
from topgun.models.okx import OKXDataStore
from topgun.models.phemex import PhemexDataStore
from topgun.store import DataStore, DataStoreCollection, StoreChange, StoreStream
from topgun.ws import WebSocketApp, WebSocketQueue

__all__: tuple[str, ...] = (
    # version
    "__version__",
    # client
    "Client",
    "FetchResult",
    "NotJSONContent",
    # ws
    "WebSocketApp",
    "WebSocketQueue",
    # store
    "DataStore",
    "DataStoreCollection",
    "StoreChange",
    "StoreStream",
    # models
    "BinanceCOINMDataStore",
    "BinanceSpotDataStore",
    "BinanceUSDSMDataStore",
    "BitMEXDataStore",
    "BitgetV2DataStore",
    "BitgetDataStore",
    "BybitDataStore",
    "CoincheckDataStore",
    "GMOCoinDataStore",
    "HyperliquidDataStore",
    "KuCoinDataStore",
    "OKXDataStore",
    "PhemexDataStore",
    "bitFlyerDataStore",
    "bitbankDataStore",
    "bitbankPrivateDataStore",
    # auth
    "Auth",
)
