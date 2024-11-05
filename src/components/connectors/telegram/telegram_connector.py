import os
from typing import Optional, List, Any

from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class TelegramConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "TelegramConnector",
            description: Optional[str] = None,
            token: Optional[str] = None,
            chat_id: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True,
            parse_mode: Optional[str] = None
    ):
        """
        Initializes the TelegramConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Telegram Connector for sending messages",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.parse_mode = parse_mode
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
        self._last_data = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with Telegram API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to Telegram API for chat ID: {self.chat_id}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Telegram connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Telegram")
            raise

    def disconnect(self) -> None:
        """Disconnects from Telegram API."""
        try:
            log.info(f"Disconnecting from Telegram for chat ID: {self.chat_id}")
            self.connected = False
            self.session.close()
        except Exception as e:
            self._handle_exception(e, "Error during Telegram disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the Telegram connection."""
        try:
            if not self.token or not self.chat_id:
                return False

            response = self.session.get(
                f"{self.base_url}/getMe",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Telegram connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']

    def send_message(self, message: str) -> bool:
        """Sends a message through Telegram."""
        if not self.connected:
            raise ConnectionError("Not connected to Telegram")

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": str(self.chat_id),
                "text": message
            }

            if self.parse_mode:
                payload["parse_mode"] = self.parse_mode

            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send Telegram message: {str(e)}")
            return False

    def process_data(self, data: Any) -> str:
        """Processes data before sending to Telegram."""
        if isinstance(data, dict):
            return "\n".join([f"{k}: {v}" for k, v in data.items()])
        elif isinstance(data, (list, tuple)):
            return "\n".join(map(str, data))
        return str(data)

    def send_data(self, data: Any) -> bool:
        """Processes and sends data through Telegram."""
        try:
            processed_message = self.process_data(data)
            return self.send_message(processed_message)
        except Exception as e:
            self._handle_exception(e, "Error processing and sending data")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Workflow notification from {self.name}"
            return self.send_message(message or default_message)
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False