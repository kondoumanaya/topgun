import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import aiohttp

from bots.gmo_board_watcher.main import GMOBoardWatcher, main


def test_gmo_board_watcher_init():
    """Test GMO board watcher initialization"""
    watcher = GMOBoardWatcher("BTC_JPY")
    assert watcher.symbol == "BTC_JPY"
    assert watcher.session is None
    assert watcher.ws is None
    assert watcher.running is False


def test_gmo_board_watcher_custom_symbol():
    """Test GMO board watcher with custom symbol"""
    watcher = GMOBoardWatcher("ETH_JPY")
    assert watcher.symbol == "ETH_JPY"


def test_gmo_board_watcher_default_symbol():
    """Test GMO board watcher with default symbol"""
    watcher = GMOBoardWatcher()
    assert watcher.symbol == "BTC_JPY"


@pytest.mark.asyncio
async def test_gmo_board_watcher_cleanup():
    """Test GMO board watcher cleanup"""
    watcher = GMOBoardWatcher("BTC_JPY")
    watcher.running = True
    
    mock_ws = AsyncMock()
    mock_session = AsyncMock()
    watcher.ws = mock_ws
    watcher.session = mock_session
    
    await watcher.cleanup()
    
    assert watcher.running is False
    mock_ws.close.assert_called_once()
    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_gmo_board_watcher_cleanup_no_connections():
    """Test GMO board watcher cleanup with no connections"""
    watcher = GMOBoardWatcher("BTC_JPY")
    watcher.running = True
    
    await watcher.cleanup()
    
    assert watcher.running is False


@pytest.mark.asyncio
async def test_gmo_board_watcher_stop():
    """Test GMO board watcher stop"""
    watcher = GMOBoardWatcher("BTC_JPY")
    watcher.running = True
    
    await watcher.stop()
    
    assert watcher.running is False


@pytest.mark.asyncio
async def test_handle_message():
    """Test message handling"""
    watcher = GMOBoardWatcher("BTC_JPY")
    
    test_data = {
        "channel": "orderbooks",
        "symbol": "BTC_JPY",
        "asks": [["100", "1.0"]],
        "bids": [["99", "1.0"]],
        "timestamp": "2023-01-01T00:00:00Z"
    }
    
    await watcher._handle_message(test_data)


@pytest.mark.asyncio
async def test_handle_message_wrong_symbol():
    """Test message handling with wrong symbol"""
    watcher = GMOBoardWatcher("BTC_JPY")
    
    test_data = {
        "channel": "orderbooks",
        "symbol": "ETH_JPY",
        "asks": [["100", "1.0"]],
        "bids": [["99", "1.0"]],
        "timestamp": "2023-01-01T00:00:00Z"
    }
    
    await watcher._handle_message(test_data)


@pytest.mark.asyncio
async def test_handle_message_wrong_channel():
    """Test message handling with wrong channel"""
    watcher = GMOBoardWatcher("BTC_JPY")
    
    test_data = {
        "channel": "ticker",
        "symbol": "BTC_JPY",
        "price": "100"
    }
    
    await watcher._handle_message(test_data)


@pytest.mark.asyncio
async def test_handle_message_empty_data():
    """Test message handling with empty data"""
    watcher = GMOBoardWatcher("BTC_JPY")
    
    test_data = {
        "channel": "orderbooks",
        "symbol": "BTC_JPY",
    }
    
    await watcher._handle_message(test_data)


@pytest.mark.asyncio
async def test_start_websocket_connection():
    """Test WebSocket connection setup"""
    watcher = GMOBoardWatcher("BTC_JPY")
    
    mock_session = AsyncMock()
    mock_ws = AsyncMock()
    mock_ws.send_str = AsyncMock()
    
    mock_msg = MagicMock()
    mock_msg.type = aiohttp.WSMsgType.TEXT
    mock_msg.data = json.dumps({
        "channel": "orderbooks",
        "symbol": "BTC_JPY",
        "asks": [["100", "1.0"]],
        "bids": [["99", "1.0"]],
        "timestamp": "2023-01-01T00:00:00Z"
    })
    
    async def mock_aiter(self):
        yield mock_msg
        watcher.running = False
    
    mock_ws.__aiter__ = mock_aiter
    mock_session.ws_connect.return_value = mock_ws
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await watcher.start()
    
    mock_session.ws_connect.assert_called_once_with("wss://api.coin.z.com/ws/public/v1")
    mock_ws.send_str.assert_called_once()


@pytest.mark.asyncio
async def test_start_websocket_error():
    """Test WebSocket connection with error"""
    watcher = GMOBoardWatcher("BTC_JPY")
    
    mock_session = AsyncMock()
    mock_ws = AsyncMock()
    mock_ws.send_str = AsyncMock()
    
    mock_msg = MagicMock()
    mock_msg.type = aiohttp.WSMsgType.ERROR
    mock_ws.exception.return_value = Exception("WebSocket error")
    
    async def mock_aiter(self):
        yield mock_msg
    
    mock_ws.__aiter__ = mock_aiter
    mock_session.ws_connect.return_value = mock_ws
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await watcher.start()
    
    mock_session.ws_connect.assert_called_once()


@pytest.mark.asyncio
async def test_start_json_decode_error():
    """Test WebSocket with JSON decode error"""
    watcher = GMOBoardWatcher("BTC_JPY")
    
    mock_session = AsyncMock()
    mock_ws = AsyncMock()
    mock_ws.send_str = AsyncMock()
    
    mock_msg = MagicMock()
    mock_msg.type = aiohttp.WSMsgType.TEXT
    mock_msg.data = "invalid json"
    
    async def mock_aiter(self):
        yield mock_msg
        watcher.running = False
    
    mock_ws.__aiter__ = mock_aiter
    mock_session.ws_connect.return_value = mock_ws
    
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await watcher.start()
    
    mock_session.ws_connect.assert_called_once()


@pytest.mark.asyncio
async def test_start_exception():
    """Test start method with exception"""
    watcher = GMOBoardWatcher("BTC_JPY")
    
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session_class.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection failed"):
            await watcher.start()


@pytest.mark.asyncio
async def test_main_function():
    """Test main function"""
    with patch.dict(os.environ, {"GMO_SYMBOL": "ETH_JPY"}):
        with patch("bots.gmo_board_watcher.main.GMOBoardWatcher") as mock_watcher_class:
            mock_watcher = AsyncMock()
            mock_watcher_class.return_value = mock_watcher
            mock_watcher.start.side_effect = KeyboardInterrupt()
            
            await main()
            
            mock_watcher_class.assert_called_once_with(symbol="ETH_JPY")
            mock_watcher.start.assert_called_once()
            mock_watcher.cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_main_function_default_symbol():
    """Test main function with default symbol"""
    with patch("bots.gmo_board_watcher.main.GMOBoardWatcher") as mock_watcher_class:
        mock_watcher = AsyncMock()
        mock_watcher_class.return_value = mock_watcher
        mock_watcher.start.side_effect = KeyboardInterrupt()
        
        await main()
        
        mock_watcher_class.assert_called_once_with(symbol="BTC_JPY")


@pytest.mark.asyncio
async def test_main_function_exception():
    """Test main function with exception"""
    with patch("bots.gmo_board_watcher.main.GMOBoardWatcher") as mock_watcher_class:
        mock_watcher = AsyncMock()
        mock_watcher_class.return_value = mock_watcher
        mock_watcher.start.side_effect = Exception("Test error")
        
        with patch("sys.exit") as mock_exit:
            await main()
            mock_exit.assert_called_once_with(1)
