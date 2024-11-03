# File: pipedrive_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class PipedriveConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "PipedriveConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            api_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the PipedriveConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Pipedrive integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('PIPEDRIVE_BASE_URL', 'https://api.pipedrive.com/v1')
        self.api_token = api_token or os.getenv('PIPEDRIVE_API_TOKEN')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Pipedrive API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Pipedrive API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Pipedrive connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Pipedrive")
            raise

    def disconnect(self) -> None:
        """Disconnects from Pipedrive API."""
        try:
            log.info("Disconnecting from Pipedrive API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Pipedrive disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Pipedrive API."""
        try:
            if not self.base_url or not self.api_token:
                return False
            url = f"{self.base_url}/users/me?api_token={self.api_token}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Pipedrive connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['PIPEDRIVE_BASE_URL', 'PIPEDRIVE_API_TOKEN']

    def create_deal(self, deal_data: Dict[str, Any]) -> bool:
        """Creates a new deal in Pipedrive."""
        if not self.connected:
            raise ConnectionError("Not connected to Pipedrive API")

        try:
            url = f"{self.base_url}/deals?api_token={self.api_token}"
            response = requests.post(url, json=deal_data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created deal in Pipedrive")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create deal in Pipedrive")
            return False

    def get_deals(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Gets deals from Pipedrive based on provided filters."""
        if not self.connected:
            raise ConnectionError("Not connected to Pipedrive API")

        try:
            url = f"{self.base_url}/deals?api_token={self.api_token}"
            response = requests.get(url, headers=self.headers, params=filters, timeout=self.timeout)
            response.raise_for_status()
            deals = response.json().get('data', [])
            log.info("Successfully retrieved deals from Pipedrive")
            return deals
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve deals from Pipedrive")
            return []

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False