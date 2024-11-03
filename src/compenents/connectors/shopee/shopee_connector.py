# File: shopee_connector.py
import os
import requests
from typing import Optional, List, Dict, Any
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class ShopeeConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "ShopeeConnector",
            description: Optional[str] = None,
            partner_id: Optional[str] = None,
            shop_id: Optional[str] = None,
            access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the ShopeeConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Shopee API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.partner_id = partner_id or os.getenv('SHOPEE_PARTNER_ID')
        self.shop_id = shop_id or os.getenv('SHOPEE_SHOP_ID')
        self.access_token = access_token or os.getenv('SHOPEE_ACCESS_TOKEN')
        self.base_url = "https://partner.shopeemobile.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Shopee API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Shopee API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Shopee connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Shopee API")
            raise

    def disconnect(self) -> None:
        """Disconnects from Shopee API."""
        try:
            log.info("Disconnecting from Shopee API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Shopee disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Shopee API."""
        try:
            if not self.access_token or not self.partner_id or not self.shop_id:
                log.error("Shopee credentials are not provided.")
                return False
            # Perform a simple request to validate the connection
            response = requests.get(f"{self.base_url}/shop/get_shop_info", headers=self.headers, timeout=self.timeout, params={"partner_id": self.partner_id, "shop_id": self.shop_id})
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Shopee connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SHOPEE_PARTNER_ID', 'SHOPEE_SHOP_ID', 'SHOPEE_ACCESS_TOKEN']

    def get_shop_info(self) -> Dict[str, Any]:
        """Fetches shop information from Shopee."""
        if not self.connected:
            raise ConnectionError("Not connected to Shopee API")

        try:
            response = requests.get(f"{self.base_url}/shop/get_shop_info", headers=self.headers, timeout=self.timeout, params={"partner_id": self.partner_id, "shop_id": self.shop_id})
            response.raise_for_status()
            log.info("Successfully fetched shop information from Shopee API")
            return response.json()
        except Exception as e:
            self._handle_exception(e, "Failed to fetch shop information from Shopee API")
            return {}

    def list_products(self) -> List[Dict[str, Any]]:
        """Lists products from the shop on Shopee."""
        if not self.connected:
            raise ConnectionError("Not connected to Shopee API")

        try:
            response = requests.get(f"{self.base_url}/product/get_item_list", headers=self.headers, timeout=self.timeout, params={"partner_id": self.partner_id, "shop_id": self.shop_id})
            response.raise_for_status()
            log.info("Successfully fetched product list from Shopee API")
            return response.json().get("response", {}).get("items", [])
        except Exception as e:
            self._handle_exception(e, "Failed to list products from Shopee API")
            return []

    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new product listing on Shopee."""
        if not self.connected:
            raise ConnectionError("Not connected to Shopee API")

        try:
            response = requests.post(f"{self.base_url}/product/add_item", headers=self.headers, json=product_data, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully created a new product on Shopee API")
            return response.json()
        except Exception as e:
            self._handle_exception(e, "Failed to create product on Shopee API")
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