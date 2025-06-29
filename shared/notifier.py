import os
import httpx
import datetime
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")

    async def send_notification(self, title: str, message: str) -> None:
        logger.info(f"📱 Notification: {title} - {message}")

        if self.discord_webhook:
            await self._send_discord(title, message)

    async def send_alert(self, message: str) -> None:
        await self.send_notification("🚨 ALERT", message)

    async def weekly_profit(self, bot: str, jpy_profit: float) -> None:
        now_utc = datetime.datetime.utcnow()
        if not (now_utc.weekday() == 6 and now_utc.hour == 15):
            return

        if self.discord_webhook:
            content = f"📈 **{bot}** week P/L: `{jpy_profit:+,.0f}` JPY"
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        self.discord_webhook,
                        json={"content": content},
                        timeout=5
                    )
                logger.info(f"📈 Weekly profit sent: {content}")
            except Exception as e:
                logger.error(f"Failed to send weekly profit: {e}")

    async def _send_discord(self, title: str, message: str) -> None:
        if not self.discord_webhook:
            return
        try:
            async with httpx.AsyncClient() as client:
                payload = {"content": f"{title}: {message}"}
                await client.post(
                    self.discord_webhook, json=payload, timeout=5
                )
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
