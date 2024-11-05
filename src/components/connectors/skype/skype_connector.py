# File: skype_connector.py
import os
from typing import Optional, List, Dict
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SkypeConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SkypeConnector",
            description: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            tenant_id: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SkypeConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Skype integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.client_id = client_id or os.getenv('SKYPE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SKYPE_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.getenv('SKYPE_TENANT_ID')
        self.token_url = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token".format(tenant_id=self.tenant_id)
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.access_token = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with Skype API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._get_access_token()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Skype API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Skype connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Skype")
            raise

    def disconnect(self) -> None:
        """Disconnects from Skype API."""
        try:
            log.info("Disconnecting from Skype API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Skype disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Skype API."""
        try:
            if not self.access_token:
                return False
            url = f"{self.base_url}/me"
            response = requests.get(url, headers=self._auth_headers(), timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Skype connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SKYPE_CLIENT_ID', 'SKYPE_CLIENT_SECRET', 'SKYPE_TENANT_ID']

    def _get_access_token(self) -> None:
        """Obtains an access token using client credentials."""
        try:
            data = {
                "client_id": self.client_id,
                "scope": "https://graph.microsoft.com/.default",
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
            response = requests.post(self.token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=self.timeout)
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            log.info("Successfully obtained access token for Skype API")
        except Exception as e:
            self._handle_exception(e, "Failed to obtain access token for Skype API")
            raise

    def _auth_headers(self) -> Dict[str, str]:
        """Returns headers with authorization for requests."""
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

    def send_message(self, chat_id: str, message: str) -> bool:
        """Sends a message to a Skype chat."""
        if not self.connected:
            raise ConnectionError("Not connected to Skype API")

        try:
            url = f"{self.base_url}/chats/{chat_id}/messages"
            payload = {
                "body": {
                    "content": message
                }
            }
            response = requests.post(url, json=payload, headers=self._auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully sent message to chat ID: {chat_id}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send message to chat ID: {chat_id}")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = "Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False