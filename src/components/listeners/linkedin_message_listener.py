# File: linkedin_message_listener.py
import os
import time
from typing import Optional, Dict, Any
import requests
from core.listener.listener_base import ListenerBase
from core.logger import log


class LinkedInMessageListener(ListenerBase):
    def __init__(
            self,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            access_token: Optional[str] = None,
            poll_interval: int = 60,  # Intervalo entre verificações em segundos
            timeout: int = 30
    ):
        super().__init__(name="LinkedInMessageListener", description="Listener for incoming LinkedIn messages")
        self.client_id = client_id or os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = access_token or os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        self.poll_interval = poll_interval
        self.timeout = timeout
        self.last_message_timestamp = None

    def authenticate(self) -> None:
        """Reauthenticate if needed and update the access token."""
        # Implementação opcional para renovação do token caso expire.
        pass

    def check_messages(self) -> Optional[Dict[str, Any]]:
        """Fetch new messages from LinkedIn messaging inbox."""
        url = f"{self.base_url}/messages"
        params = {"q": "List"}  # Ajuste conforme necessário para API
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            messages = response.json().get('elements', [])

            # Filtra mensagens novas com base no timestamp
            new_messages = [msg for msg in messages if self.is_new_message(msg)]
            return new_messages
        except Exception as e:
            log.error(f"Failed to fetch messages: {e}")
            return None

    def is_new_message(self, message: Dict[str, Any]) -> bool:
        """Check if the message is new based on timestamp."""
        timestamp = message.get("createdAt", 0)
        if self.last_message_timestamp is None or timestamp > self.last_message_timestamp:
            self.last_message_timestamp = max(self.last_message_timestamp or 0, timestamp)
            return True
        return False

    def listen(self) -> None:
        """Listen for new messages in a polling loop."""
        log.info("Starting LinkedIn message listener...")
        while True:
            new_messages = self.check_messages()
            if new_messages:
                for message in new_messages:
                    self.handle_new_message(message)
            time.sleep(self.poll_interval)

    def handle_new_message(self, message: Dict[str, Any]) -> None:
        """Handle the incoming message (e.g., log it, send a notification)."""
        sender = message.get("from", {}).get("name", "Unknown")
        content = message.get("body", {}).get("text", "")
        log.info(f"New message received from {sender}: {content}")
        # Processar mensagem conforme necessário


# Exemplo de inicialização do listener
if __name__ == "__main__":
    listener = LinkedInMessageListener(poll_interval=120)
    listener.listen()
