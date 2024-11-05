# File: mercadolivre_connector.py
import os
import requests
from typing import Optional, List, Dict, Any
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class MercadoLivreConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "MercadoLivreConnector",
            description: Optional[str] = None,
            access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the MercadoLivreConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Mercado Livre API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.access_token = access_token or os.getenv('MERCADOLIVRE_ACCESS_TOKEN')
        self.base_url = "https://api.mercadolibre.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Mercado Livre API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Mercado Livre API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Mercado Livre connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Mercado Livre API")
            raise

    def disconnect(self) -> None:
        """Disconnects from Mercado Livre API."""
        try:
            log.info("Disconnecting from Mercado Livre API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Mercado Livre disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Mercado Livre API."""
        try:
            if not self.access_token:
                log.error("Mercado Livre access token is not provided.")
                return False
            # Perform a simple request to validate the connection
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Mercado Livre connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['MERCADOLIVRE_ACCESS_TOKEN']

    def get_user_info(self) -> Dict[str, Any]:
        """Fetches the authenticated user's information from Mercado Livre."""
        if not self.connected:
            raise ConnectionError("Not connected to Mercado Livre API")

        try:
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully fetched user information from Mercado Livre API")
            return response.json()
        except Exception as e:
            self._handle_exception(e, "Failed to fetch user information from Mercado Livre API")
            return {}

    def list_items(self, user_id: str) -> List[Dict[str, Any]]:
        """Lists items of a specific user from Mercado Livre."""
        if not self.connected:
            raise ConnectionError("Not connected to Mercado Livre API")

        try:
            response = requests.get(f"{self.base_url}/users/{user_id}/items/search", headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully fetched item list from Mercado Livre API")
            return response.json().get("results", [])
        except Exception as e:
            self._handle_exception(e, "Failed to list items from Mercado Livre API")
            return []

    def create_listing(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new listing on Mercado Livre."""
        if not self.connected:
            raise ConnectionError("Not connected to Mercado Livre API")

        try:
            response = requests.post(f"{self.base_url}/items", headers=self.headers, json=listing_data, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully created a new listing on Mercado Livre API")
            return response.json()
        except Exception as e:
            self._handle_exception(e, "Failed to create listing on Mercado Livre API")
            return {}

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False