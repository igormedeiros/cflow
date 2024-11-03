# File: sap_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SAPConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SAPConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SAPConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for SAP integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('SAP_BASE_URL')
        self.client_id = client_id or os.getenv('SAP_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SAP_CLIENT_SECRET')
        self.username = username or os.getenv('SAP_USERNAME')
        self.password = password or os.getenv('SAP_PASSWORD')
        self.access_token = None

        if not self.base_url or not self.client_id or not self.client_secret:
            raise ValueError("SAP base URL, client ID, and client secret must be provided for SAPConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to SAP by retrieving an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._get_access_token()
            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to SAP at: {self.base_url}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate SAP connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to SAP")
            raise

    def _get_access_token(self) -> None:
        """Retrieves an OAuth2 access token from SAP."""
        try:
            url = f"{self.base_url}/oauth/token"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            self.access_token = response.json().get('access_token')
            log.info("Successfully retrieved access token for SAP")
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve access token for SAP")
            raise

    def disconnect(self) -> None:
        """Disconnects from SAP by invalidating the access token."""
        try:
            log.info("Disconnecting from SAP")
            self.access_token = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during SAP disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if SAP connection is successful by checking the access token."""
        if self.access_token:
            log.info("SAP connection validated successfully")
            return True
        else:
            log.error("SAP connection validation failed: No access token available")
            return False

    def get_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetches data from the specified SAP endpoint."""
        if not self.connected or not self.access_token:
            raise ConnectionError("Not connected to SAP")

        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched data from SAP endpoint '{endpoint}'")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch data from SAP endpoint '{endpoint}'")
            raise

    def post_data(self, endpoint: str, data: Dict[str, Any]) -> None:
        """Sends data to the specified SAP endpoint."""
        if not self.connected or not self.access_token:
            raise ConnectionError("Not connected to SAP")

        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully posted data to SAP endpoint '{endpoint}'")
        except Exception as e:
            self._handle_exception(e, f"Failed to post data to SAP endpoint '{endpoint}'")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for SAP connection."""
        return ['SAP_BASE_URL', 'SAP_CLIENT_ID', 'SAP_CLIENT_SECRET', 'SAP_USERNAME', 'SAP_PASSWORD']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False