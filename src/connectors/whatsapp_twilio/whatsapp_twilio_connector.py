# File: whatsapp_twilio_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class WhatsAppTwilioConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "WhatsAppTwilioConnector",
            description: Optional[str] = None,
            account_sid: Optional[str] = None,
            auth_token: Optional[str] = None,
            from_phone_number: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the WhatsAppTwilioConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for WhatsApp Twilio API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_phone_number = from_phone_number or os.getenv('TWILIO_WHATSAPP_FROM')
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Twilio API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Twilio API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Twilio connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Twilio")
            raise

    def disconnect(self) -> None:
        """Disconnects from Twilio API."""
        try:
            log.info("Disconnecting from Twilio API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Twilio disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Twilio API."""
        try:
            if not self.account_sid or not self.auth_token:
                return False
            response = requests.get(
                f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}.json",
                auth=(self.account_sid, self.auth_token),
                headers=self.headers,
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Twilio connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_WHATSAPP_FROM']

    def send_message(self, to_phone_number: str, message: str) -> bool:
        """Sends a message through WhatsApp Twilio API to a specified phone number."""
        if not self.connected:
            raise ConnectionError("Not connected to Twilio API")

        try:
            payload = {
                "To": f"whatsapp:{to_phone_number}",
                "From": f"whatsapp:{self.from_phone_number}",
                "Body": message
            }
            response = requests.post(
                self.base_url,
                data=payload,
                auth=(self.account_sid, self.auth_token),
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            log.info(f"Successfully sent message to phone number: {to_phone_number}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send message to phone number: {to_phone_number}")
            return False

    def send_media_message(self, to_phone_number: str, media_url: str, caption: Optional[str] = None) -> bool:
        """Sends a media message through WhatsApp Twilio API to a specified phone number."""
        if not self.connected:
            raise ConnectionError("Not connected to Twilio API")

        try:
            payload = {
                "To": f"whatsapp:{to_phone_number}",
                "From": f"whatsapp:{self.from_phone_number}",
                "Body": caption or "",
                "MediaUrl": media_url
            }
            response = requests.post(
                self.base_url,
                data=payload,
                auth=(self.account_sid, self.auth_token),
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            log.info(f"Successfully sent media message to phone number: {to_phone_number}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send media message to phone number: {to_phone_number}")
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