# File: kiwify_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class KiwifyConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "KiwifyConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the KiwifyConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Kiwify integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('KIWIFY_BASE_URL', 'https://api.kiwify.com')
        self.client_id = client_id or os.getenv('KIWIFY_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('KIWIFY_CLIENT_SECRET')
        self.access_token = access_token or os.getenv('KIWIFY_ACCESS_TOKEN')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Kiwify API and obtains an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Kiwify API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Kiwify connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Kiwify")
            raise

    def disconnect(self) -> None:
        """Disconnects from Kiwify API."""
        try:
            log.info("Disconnecting from Kiwify API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Kiwify disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Kiwify API."""
        try:
            if not self.base_url or not self.access_token:
                return False
            url = f"{self.base_url}/accounts/v1/me"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Kiwify connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['KIWIFY_BASE_URL', 'KIWIFY_CLIENT_ID', 'KIWIFY_CLIENT_SECRET', 'KIWIFY_ACCESS_TOKEN']

    def get_sales(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Gets sales data from Kiwify based on provided filters."""
        if not self.connected:
            raise ConnectionError("Not connected to Kiwify API")

        try:
            url = f"{self.base_url}/mykiwify/v1/sales"
            response = requests.get(url, headers=self.headers, params=filters, timeout=self.timeout)
            response.raise_for_status()
            sales = response.json().get('items', [])
            log.info("Successfully retrieved sales from Kiwify")
            return sales
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve sales from Kiwify")
            return []

    def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        """Gets subscription details by subscription ID from Kiwify."""
        if not self.connected:
            raise ConnectionError("Not connected to Kiwify API")

        try:
            url = f"{self.base_url}/mykiwify/v1/subscriptions/{subscription_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            subscription_details = response.json()
            log.info(f"Successfully retrieved subscription details for ID: {subscription_id}")
            return subscription_details
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve subscription details for ID: {subscription_id}")
            return {}

    def create_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Creates a webhook subscription in Kiwify."""
        if not self.connected:
            raise ConnectionError("Not connected to Kiwify API")

        try:
            url = f"{self.base_url}/webhook/v1/subscription"
            response = requests.post(url, json=webhook_data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully created webhook subscription in Kiwify")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create webhook in Kiwify")
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