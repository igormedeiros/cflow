# File: rest_api_connector.py
import os
from typing import Optional, List, Any, Dict
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class RestAPIConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "RestAPIConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the RestAPIConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for REST API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('REST_API_BASE_URL')
        self.headers = headers or {'Content-Type': 'application/json'}

    def connect(self, **kwargs) -> None:
        """Establishes connection to the REST API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to REST API at: {self.base_url}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate REST API connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to REST API")
            raise

    def disconnect(self) -> None:
        """Disconnects from the REST API."""
        try:
            log.info(f"Disconnecting from REST API at: {self.base_url}")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during REST API disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to the REST API."""
        try:
            if not self.base_url:
                return False

            response = requests.get(f"{self.base_url}/health", headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "REST API connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['REST_API_BASE_URL']

    def send_request(self, endpoint: str, method: str = 'GET', params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Any:
        """Sends a request to the REST API.

        :param endpoint: The endpoint to send the request to.
        :param method: HTTP method (GET, POST, PUT, DELETE).
        :param params: Query parameters for the request.
        :param data: Data to be sent in the body of the request.
        :return: Response from the REST API.
        """
        if not self.connected:
            raise ConnectionError("Not connected to REST API")

        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.request(method, url, headers=self.headers, params=params, json=data, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully sent {method} request to {url}")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to send {method} request to {endpoint}: {str(e)}")
            return None

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            response = self.send_request(endpoint="notify", method="POST", data=message or default_message)
            return response is not None
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False