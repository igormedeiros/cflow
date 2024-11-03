# File: hotmart_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class HotmartConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "HotmartConnector",
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
        Initializes the HotmartConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Hotmart integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('HOTMART_BASE_URL', 'https://api.hotmart.com')
        self.client_id = client_id or os.getenv('HOTMART_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('HOTMART_CLIENT_SECRET')
        self.access_token = access_token or os.getenv('HOTMART_ACCESS_TOKEN')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Hotmart API and obtains an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Hotmart API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Hotmart connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Hotmart")
            raise

    def disconnect(self) -> None:
        """Disconnects from Hotmart API."""
        try:
            log.info("Disconnecting from Hotmart API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Hotmart disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Hotmart API."""
        try:
            if not self.base_url or not self.access_token:
                return False
            url = f"{self.base_url}/payments/api/v1/user/me"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Hotmart connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['HOTMART_BASE_URL', 'HOTMART_CLIENT_ID', 'HOTMART_CLIENT_SECRET', 'HOTMART_ACCESS_TOKEN']

    def get_sales(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Gets sales data from Hotmart based on provided filters."""
        if not self.connected:
            raise ConnectionError("Not connected to Hotmart API")

        try:
            url = f"{self.base_url}/payments/api/v1/sales"
            response = requests.get(url, headers=self.headers, params=filters, timeout=self.timeout)
            response.raise_for_status()
            sales = response.json().get('items', [])
            log.info("Successfully retrieved sales from Hotmart")
            return sales
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve sales from Hotmart")
            return []

    def get_transactions(self, transaction_id: str) -> Dict[str, Any]:
        """Gets transaction details by transaction ID from Hotmart."""
        if not self.connected:
            raise ConnectionError("Not connected to Hotmart API")

        try:
            url = f"{self.base_url}/payments/api/v1/transactions/{transaction_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            transaction = response.json()
            log.info(f"Successfully retrieved transaction details for ID: {transaction_id}")
            return transaction
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve transaction details for ID: {transaction_id}")
            return {}

    def create_refund(self, transaction_id: str, refund_data: Dict[str, Any]) -> bool:
        """Creates a refund request for a given transaction in Hotmart."""
        if not self.connected:
            raise ConnectionError("Not connected to Hotmart API")

        try:
            url = f"{self.base_url}/payments/api/v1/transactions/{transaction_id}/refund"
            response = requests.post(url, json=refund_data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created refund for transaction ID: {transaction_id}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to create refund for transaction ID: {transaction_id}")
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