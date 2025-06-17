"""
Type stubs for topgun main module
"""
from typing import Any, Dict

from topgun.client import Client as Client

class bitbankPrivateDataStore:
    """bitbank private data store"""
    spot_order: Any

    async def initialize(self, response: Any) -> None: ...
    async def onmessage(self, message: Dict[str, Any]) -> None: ...

    def watch(self) -> Any: ...
    def find(self) -> Any: ...

# Re-export important classes
__all__ = ["Client", "bitbankPrivateDataStore"]
