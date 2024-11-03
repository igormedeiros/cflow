# File: twilio_connector.py
import os
from typing import Optional, List, Any
from twilio.rest import Client
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class TwilioConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "TwilioConnector",
            description: Optional[str] = None,
            account_sid: Optional[str] = None,
            auth_token: Optional[str] = None,
            from_phone: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the TwilioConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Twilio integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_phone = from_phone or os.getenv('TWILIO_FROM_PHONE')
        self.client = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with Twilio API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            self.client = Client(self.account_sid, self.auth_token)

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to Twilio with SID: {self.account_sid}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Twilio connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Twilio")
            raise

    def disconnect(self) -> None:
        """Disconnects from Twilio API."""
        try:
            log.info(f"Disconnecting from Twilio with SID: {self.account_sid}")
            self.connected = False
            self.client = None
        except Exception as e:
            self._handle_exception(e, "Error during Twilio disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Twilio API."""
        try:
            if not self.account_sid or not self.auth_token:
                return False

            # Attempt to fetch account details to validate the connection
            account = self.client.api.accounts(self.account_sid).fetch()
            return account.status == 'active'
        except Exception as e:
            self._handle_exception(e, "Twilio connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_PHONE']

    def send_sms(self, to_phone: str, message: str) -> bool:
        """Sends an SMS to a specified phone number."""
        if not self.connected:
            raise ConnectionError("Not connected to Twilio")

        try:
            message_instance = self.client.messages.create(
                body=message,
                from_=self.from_phone,
                to=to_phone
            )
            log.info(f"Successfully sent SMS to {to_phone}. SID: {message_instance.sid}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send SMS to {to_phone}: {str(e)}")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            return self.send_sms(to_phone=self.from_phone, message=message or default_message)
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False
