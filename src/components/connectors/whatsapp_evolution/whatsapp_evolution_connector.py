# File: whatsapp_evolution_connector.py
import os
from typing import Optional, List
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class WhatsAppEvolutionConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "WhatsAppEvolutionConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the WhatsAppEvolutionConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for WhatsApp Evolution API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('WHATSAPP_EVOLUTION_BASE_URL', 'https://api.whatsapp-evolution.com')
        self.api_key = api_key or os.getenv('WHATSAPP_EVOLUTION_API_KEY')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with WhatsApp Evolution API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to WhatsApp Evolution API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate WhatsApp Evolution connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to WhatsApp Evolution")
            raise

    def disconnect(self) -> None:
        """Disconnects from WhatsApp Evolution API."""
        try:
            log.info("Disconnecting from WhatsApp Evolution API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during WhatsApp Evolution disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to WhatsApp Evolution API."""
        try:
            if not self.base_url or not self.api_key:
                return False
            url = f"{self.base_url}/status"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "WhatsApp Evolution connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['WHATSAPP_EVOLUTION_BASE_URL', 'WHATSAPP_EVOLUTION_API_KEY']

    def send_message(self, phone_number: str, message: str) -> bool:
        """Sends a message through WhatsApp Evolution API to a specified phone number."""
        if not self.connected:
            raise ConnectionError("Not connected to WhatsApp Evolution API")

        try:
            url = f"{self.base_url}/send-message"
            payload = {
                "phone": phone_number,
                "message": message
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully sent message to phone number: {phone_number}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send message to phone number: {phone_number}")
            return False

    def send_media_message(self, phone_number: str, media_url: str, caption: Optional[str] = None) -> bool:
        """Sends a media message through WhatsApp Evolution API to a specified phone number."""
        if not self.connected:
            raise ConnectionError("Not connected to WhatsApp Evolution API")

        try:
            url = f"{self.base_url}/send-media"
            payload = {
                "phone": phone_number,
                "media_url": media_url,
                "caption": caption
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully sent media message to phone number: {phone_number}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send media message to phone number: {phone_number}")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False