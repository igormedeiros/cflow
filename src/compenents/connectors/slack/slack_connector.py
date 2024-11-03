# File: slack_connector.py
import os
from typing import Optional, List
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SlackConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SlackConnector",
            description: Optional[str] = None,
            token: Optional[str] = None,
            channel: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SlackConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Slack integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.token = token or os.getenv('SLACK_BOT_TOKEN')
        self.channel = channel or os.getenv('SLACK_CHANNEL')
        self.base_url = "https://slack.com/api"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Slack API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to Slack for channel: {self.channel}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Slack connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Slack")
            raise

    def disconnect(self) -> None:
        """Disconnects from Slack API."""
        try:
            log.info(f"Disconnecting from Slack for channel: {self.channel}")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Slack disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Slack API."""
        try:
            if not self.token or not self.channel:
                return False

            response = requests.get(
                f"{self.base_url}/auth.test",
                headers=self.headers,
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Slack connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SLACK_BOT_TOKEN', 'SLACK_CHANNEL']

    def send_message(self, message: str) -> bool:
        """Sends a message to a Slack channel."""
        if not self.connected:
            raise ConnectionError("Not connected to Slack")

        try:
            url = f"{self.base_url}/chat.postMessage"
            payload = {
                "channel": self.channel,
                "text": message
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully sent message to Slack channel: {self.channel}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send message to Slack: {str(e)}")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            return self.send_message(message or default_message)
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False
