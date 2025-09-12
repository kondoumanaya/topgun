"""
Complete type stubs for topgun.helpers.bitbank
"""
from typing import Any, Callable, Coroutine, Dict, List, Optional

# Forward declaration to avoid circular imports
class Client: ...

async def subscribe_with_callback(
    client: Client,
    callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]
) -> None:
    """Subscribe to bitbank WebSocket with callback"""
    ...

# Additional functions (if they exist)
async def get_balance(client: Client) -> Dict[str, Any]: ...
async def get_active_orders(client: Client, pair: Optional[str] = None) -> List[Dict[str, Any]]: ...
async def place_order(client: Client, pair: str, amount: str, price: str, side: str, type: str) -> Dict[str, Any]: ...
async def cancel_order(client: Client, pair: str, order_id: int) -> Dict[str, Any]: ...
