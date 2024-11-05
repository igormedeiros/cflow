# File: sugarcrm_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SugarCRMConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SugarCRMConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SugarCRMConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for SugarCRM integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('SUGARCRM_BASE_URL')
        self.username = username or os.getenv('SUGARCRM_USERNAME')
        self.password = password or os.getenv('SUGARCRM_PASSWORD')
        self.client_id = client_id or os.getenv('SUGARCRM_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SUGARCRM_CLIENT_SECRET')
        self.access_token = None
        self.headers = {
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with SugarCRM API and obtains an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to SugarCRM API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate SugarCRM connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to SugarCRM")
            raise

    def disconnect(self) -> None:
        """Disconnects from SugarCRM API."""
        try:
            log.info("Disconnecting from SugarCRM API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during SugarCRM disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to SugarCRM API by obtaining an access token."""
        try:
            if not self.base_url or not self.username or not self.password or not self.client_id or not self.client_secret:
                return False
            url = f"{self.base_url}/oauth2/token"
            data = {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password
            }
            response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            self.access_token = response.json().get('access_token')
            self.headers["Authorization"] = f"Bearer {self.access_token}"
            return True
        except Exception as e:
            self._handle_exception(e, "SugarCRM connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SUGARCRM_BASE_URL', 'SUGARCRM_USERNAME', 'SUGARCRM_PASSWORD', 'SUGARCRM_CLIENT_ID', 'SUGARCRM_CLIENT_SECRET']

    def create_record(self, module: str, record_data: Dict[str, Any]) -> bool:
        """Creates a new record in the specified SugarCRM module."""
        if not self.connected:
            raise ConnectionError("Not connected to SugarCRM API")

        try:
            url = f"{self.base_url}/rest/v11/{module}"
            response = requests.post(url, json=record_data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created record in SugarCRM module: {module}")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create record in SugarCRM")
            return False

    def get_records(self, module: str, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Gets records from SugarCRM based on the provided filters."""
        if not self.connected:
            raise ConnectionError("Not connected to SugarCRM API")

        try:
            url = f"{self.base_url}/rest/v11/{module}"
            response = requests.get(url, headers=self.headers, params=filters, timeout=self.timeout)
            response.raise_for_status()
            records = response.json().get('records', [])
            log.info(f"Successfully retrieved records from SugarCRM module: {module}")
            return records
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve records from SugarCRM")
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