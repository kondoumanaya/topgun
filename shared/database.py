import aiosqlite
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_path = os.getenv("SQLITE_PATH", "/data/bot.db")
        self.connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:

        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        logger.info(f"🗄️ SQLite connected: {self.db_path}")

    async def _create_tables(self) -> None:
        if self.connection is None:
            raise RuntimeError("Database not connected")
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                signature TEXT
            )
        """)
        await self.connection.commit()

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
            logger.info("🗄️ SQLite connection closed")

    async def log_order(self, order_data: Dict[str, Any]) -> None:
        if not self.connection:
            logger.warning("Database not connected")
            return

        await self.connection.execute("""
            INSERT INTO orders (symbol, side, quantity, price, signature)
            VALUES (?, ?, ?, ?, ?)
        """, (
            order_data.get("symbol"),
            order_data.get("side"),
            order_data.get("quantity"),
            order_data.get("price"),
            order_data.get("signature")
        ))
        await self.connection.commit()
        logger.info(f"📝 Order logged to SQLite: {order_data}")
