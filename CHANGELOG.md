# Changelog

All notable changes to the topgun library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-14

### Added
- Initial release of topgun library
- HTTP/WebSocket client with automatic authentication
- DataStore for real-time data management
- Hyperliquid EIP-712 signing helpers
- Support for multiple cryptocurrency exchanges
- Automatic reconnection and heartbeat for WebSocket connections
- Built on aiohttp for async operations

### Features
- `topgun.Client` - HTTP/WebSocket client with authentication
- `topgun.WebSocketApp` - WebSocket connection management
- `topgun.DataStore` - Real-time data handling
- `topgun.helpers.hyperliquid` - Hyperliquid-specific signing functions
- Support for Binance, Bitflyer, Bybit, OKX, and other exchanges

### Dependencies
- aiohttp>=3.7 - HTTP/WebSocket client functionality
- typing-extensions>=3.10 - Type hints for Python <3.10

[0.1.0]: https://github.com/kondoumanaya/topgun/releases/tag/v0.1.0
