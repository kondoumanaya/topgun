"""Notification management for trading bots"""
import asyncio
import logging
from typing import Optional
import aiohttp
import os

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages notifications across multiple channels"""

    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")

    async def send_notification(self, title: str, message: str) -> None:
        """Send notification to configured channels"""
        logger.info(f"📱 Notification: {title} - {message}")

        tasks = []
        if self.slack_webhook:
            tasks.append(self._send_slack(title, message))
        if self.discord_webhook:
            tasks.append(self._send_discord(title, message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_alert(self, message: str) -> None:
        """Send high-priority alert"""
        await self.send_notification("🚨 ALERT", message)

    async def _send_slack(self, title: str, message: str) -> None:
        """Send to Slack webhook"""
        if not self.slack_webhook:
            return
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"text": f"{title}: {message}"}
                await session.post(self.slack_webhook, json=payload)
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    async def _send_discord(self, title: str, message: str) -> None:
        """Send to Discord webhook"""
        if not self.discord_webhook:
            return
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"content": f"{title}: {message}"}
                await session.post(self.discord_webhook, json=payload)
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")