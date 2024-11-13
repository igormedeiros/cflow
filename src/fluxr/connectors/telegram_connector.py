from typing import Optional
from telegram.ext import ApplicationBuilder
from ..base import Connector

class TelegramConnector(Connector):
    def __init__(self, name: str = "TelegramConnector"):
        super().__init__(name=name)
        self.app = None
        
    async def initialize(self) -> None:
        """Initialize the Telegram connector."""
        token = self.connection_params.get("token")
        if not token:
            raise ValueError("Telegram bot token not provided")
        self.app = ApplicationBuilder().token(token).build()
        
    async def connect(self) -> None:
        """Start Telegram bot."""
        if not self.app:
            raise RuntimeError("Telegram bot not initialized")
        await self.app.initialize()
        
    async def disconnect(self) -> None:
        """Stop Telegram bot."""
        if self.app:
            await self.app.shutdown()
            
    async def send_message(self, chat_id: int, text: str) -> None:
        """Send message to Telegram chat."""
        if not self.app:
            raise RuntimeError("Telegram bot not connected")
        await self.app.bot.send_message(chat_id=chat_id, text=text)