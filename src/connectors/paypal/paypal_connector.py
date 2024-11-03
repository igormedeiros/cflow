# File: paypal_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class PayPalConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "PayPalConnector",
            description: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the PayPalConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for PayPal integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.client_id = client_id or os.getenv('PAYPAL_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('PAYPAL_CLIENT_SECRET')
        self.token_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
        self.base_url = "https://api.sandbox.paypal.com/v1"
        self.access_token = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with PayPal API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._get_access_token()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to PayPal API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate PayPal connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to PayPal")
            raise

    def disconnect(self) -> None:
        """Disconnects from PayPal API."""
        try:
            log.info("Disconnecting from PayPal API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during PayPal disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to PayPal API."""
        try:
            if not self.access_token:
                return False
            url = f"{self.base_url}/payments/payment"
            response = requests.get(url, headers=self._auth_headers(), timeout=self.timeout)
            return response.status_code == 200 or response.status_code == 401
        except Exception as e:
            self._handle_exception(e, "PayPal connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['PAYPAL_CLIENT_ID', 'PAYPAL_CLIENT_SECRET']

    def _get_access_token(self) -> None:
        """Obtains an access token using client credentials."""
        try:
            auth = (self.client_id, self.client_secret)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {"grant_type": "client_credentials"}
            response = requests.post(self.token_url, auth=auth, headers=headers, data=data, timeout=self.timeout)
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            log.info("Successfully obtained access token for PayPal API")
        except Exception as e:
            self._handle_exception(e, "Failed to obtain access token for PayPal API")
            raise

    def _auth_headers(self) -> Dict[str, str]:
        """Returns headers with authorization for requests."""
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a payment through PayPal API."""
        if not self.connected:
            raise ConnectionError("Not connected to PayPal API")

        try:
            url = f"{self.base_url}/payments/payment"
            response = requests.post(url, json=payment_data, headers=self._auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully created payment")
            return response.json()
        except Exception as e:
            self._handle_exception(e, "Failed to create payment in PayPal API")
            return {}

    def refund_payment(self, sale_id: str, amount: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Refunds a specific payment through PayPal API."""
        if not self.connected:
            raise ConnectionError("Not connected to PayPal API")

        try:
            url = f"{self.base_url}/payments/sale/{sale_id}/refund"
            response = requests.post(url, json=amount, headers=self._auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully refunded sale with ID: {sale_id}")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to refund sale with ID: {sale_id}")
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