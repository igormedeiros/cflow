# File: instagram_connector.py
import os
import requests
from typing import Optional, List, Dict, Any
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class InstagramConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "InstagramConnector",
            description: Optional[str] = None,
            access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the InstagramConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Instagram Graph API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.access_token = access_token or os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.base_url = "https://graph.instagram.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Instagram Graph API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Instagram Graph API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Instagram connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Instagram API")
            raise

    def disconnect(self) -> None:
        """Disconnects from Instagram API."""
        try:
            log.info("Disconnecting from Instagram API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Instagram disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Instagram Graph API."""
        try:
            if not self.access_token:
                log.error("Instagram access token is not provided.")
                return False
            # Perform a simple request to validate the connection
            response = requests.get(f"{self.base_url}/me", headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Instagram connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['INSTAGRAM_ACCESS_TOKEN']

    def get_user_info(self) -> Dict[str, Any]:
        """Fetches the authenticated user's information from Instagram."""
        if not self.connected:
            raise ConnectionError("Not connected to Instagram API")

        try:
            response = requests.get(f"{self.base_url}/me?fields=id,username,account_type", headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully fetched user information from Instagram API")
            return response.json()
        except Exception as e:
            self._handle_exception(e, "Failed to fetch user information from Instagram API")
            return {}

    def get_user_media(self) -> List[Dict[str, Any]]:
        """Fetches media items for the authenticated user from Instagram."""
        if not self.connected:
            raise ConnectionError("Not connected to Instagram API")

        try:
            response = requests.get(f"{self.base_url}/me/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp", headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully fetched user media from Instagram API")
            return response.json().get("data", [])
        except Exception as e:
            self._handle_exception(e, "Failed to fetch user media from Instagram API")
            return []

    def post_comment(self, media_id: str, message: str) -> bool:
        """Posts a comment on a specific media item on Instagram."""
        if not self.connected:
            raise ConnectionError("Not connected to Instagram API")

        try:
            url = f"{self.base_url}/{media_id}/comments"
            payload = {"message": message}
            response = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully posted comment on media {media_id}")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to post comment on Instagram media")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False