# topgun

Common library for trading bot systems providing HTTP/WebSocket clients, authentication, and helper functions.

## Installation

Install from GitHub repository with specific version:

```bash
pip install git+https://github.com/kondoumanaya/topgun.git@v0.1.0
```

For latest development version:

```bash
pip install git+https://github.com/kondoumanaya/topgun.git
```

## Features

- ✨ **HTTP / WebSocket Client**
  - Automatic authentication for private APIs
  - WebSocket automatic reconnection and heartbeat
  - Built on aiohttp for async operations

- ✨ **DataStore**
  - WebSocket message data handler
  - Processing of differential data (order book updates)
  - Real-time data management

- ✨ **Helpers**
  - Signing helpers for private APIs
  - Hyperliquid EIP-712 signing support
  - Authentication utilities

## Usage

### Basic HTTP Client

```python
import asyncio
import topgun

async def main():
    apis = {
        "exchange": ["API_KEY", "API_SECRET"]
    }
    
    async with topgun.Client(apis=apis) as client:
        result = await client.fetch("GET", "/api/endpoint")
        print(result.data)

asyncio.run(main())
```

### WebSocket Connection

```python
import asyncio
import topgun

async def message_handler(message):
    print(f"Received: {message}")

async def main():
    apis = {
        "exchange": ["API_KEY", "API_SECRET"]
    }
    
    async with topgun.Client(apis=apis) as client:
        ws = client.ws_connect(
            "wss://api.exchange.com/ws",
            hdlr_json=message_handler
        )
        await ws.wait()

asyncio.run(main())
```

### Hyperliquid Signing Helper

```python
from topgun.topgun.helpers.hyperliquid import construct_l1_action

action = {
    "type": "order",
    "orders": [{
        "a": 0,
        "b": True,
        "p": "50000",
        "s": "0.001",
        "r": False,
        "t": {"limit": {"tif": "Gtc"}}
    }]
}

domain_data, message_types, phantom_agent = construct_l1_action(
    action, nonce=1234567890, is_mainnet=False
)
```

## Version History

- **v0.1.0** - Initial release with HTTP/WebSocket client and Hyperliquid helpers
- See [CHANGELOG.md](CHANGELOG.md) for detailed version history

## Development

This library is designed to be used by multiple trading bot services. Each bot should depend on a specific tagged version for stability.

For bot template and usage examples, see the [sherrinford template repository](https://github.com/kondoumanaya/sherrinford).

## License

This project is licensed under the MIT License.
