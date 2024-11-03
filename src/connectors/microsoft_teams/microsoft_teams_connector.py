# File: microsoft_teams_connector.py
import os
import requests
from typing import Optional, List, Dict, Any
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class MicrosoftTeamsConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "MicrosoftTeamsConnector",
            description: Optional[str] = None,
            webhook_url: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the MicrosoftTeamsConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Microsoft Teams message sending",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.webhook_url = webhook_url or os.getenv('TEAMS_WEBHOOK_URL')

    def connect(self, **kwargs) -> None:
        """Establishes a connection with Microsoft Teams (via Webhook)."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Microsoft Teams")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Microsoft Teams connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Microsoft Teams")
            raise

    def disconnect(self) -> None:
        """Disconnects from Microsoft Teams (no actual disconnection needed for webhook)."""
        try:
            log.info("Disconnecting from Microsoft Teams (Webhook-based, no persistent connection)")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Microsoft Teams disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the Microsoft Teams webhook URL."""
        try:
            if not self.webhook_url:
                log.error("Microsoft Teams webhook URL is not provided.")
                return False
            return True
        except Exception as e:
            self._handle_exception(e, "Microsoft Teams connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['TEAMS_WEBHOOK_URL']

    def send_message(self, message: str, title: Optional[str] = None) -> bool:
        """Sends a message to Microsoft Teams via webhook."""
        if not self.connected:
            raise ConnectionError("Not connected to Microsoft Teams")

        try:
            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": title or "Teams Notification",
                "sections": [{
                    "activityTitle": title or "Notification from Microsoft Teams Connector",
                    "text": message
                }]
            }
            response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully sent message to Microsoft Teams")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to send message to Microsoft Teams")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            return self.send_message(message or default_message)
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False