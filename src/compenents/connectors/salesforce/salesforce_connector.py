# File: salesforce_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SalesforceConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SalesforceConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            security_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SalesforceConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Salesforce integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('SALESFORCE_BASE_URL')
        self.client_id = client_id or os.getenv('SALESFORCE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SALESFORCE_CLIENT_SECRET')
        self.username = username or os.getenv('SALESFORCE_USERNAME')
        self.password = password or os.getenv('SALESFORCE_PASSWORD')
        self.security_token = security_token or os.getenv('SALESFORCE_SECURITY_TOKEN')
        self.access_token = None
        self.headers = {
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Salesforce API and obtains an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Salesforce API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Salesforce connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Salesforce")
            raise

    def disconnect(self) -> None:
        """Disconnects from Salesforce API."""
        try:
            log.info("Disconnecting from Salesforce API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Salesforce disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Salesforce API by obtaining an access token."""
        try:
            if not self.base_url or not self.client_id or not self.client_secret or not self.username or not self.password or not self.security_token:
                return False
            url = f"{self.base_url}/services/oauth2/token"
            data = {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": f"{self.password}{self.security_token}"
            }
            response = requests.post(url, data=data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            self.access_token = response.json().get('access_token')
            self.headers["Authorization"] = f"Bearer {self.access_token}"
            return True
        except Exception as e:
            self._handle_exception(e, "Salesforce connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SALESFORCE_BASE_URL', 'SALESFORCE_CLIENT_ID', 'SALESFORCE_CLIENT_SECRET', 'SALESFORCE_USERNAME', 'SALESFORCE_PASSWORD', 'SALESFORCE_SECURITY_TOKEN']

    def create_record(self, object_type: str, record_data: Dict[str, Any]) -> bool:
        """Creates a new record in the specified Salesforce object."""
        if not self.connected:
            raise ConnectionError("Not connected to Salesforce API")

        try:
            url = f"{self.base_url}/services/data/v52.0/sobjects/{object_type}/"
            response = requests.post(url, json=record_data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created record in Salesforce object: {object_type}")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create record in Salesforce")
            return False

    def get_records(self, object_type: str, query: str) -> List[Dict[str, Any]]:
        """Gets records from Salesforce based on the provided SOQL query."""
        if not self.connected:
            raise ConnectionError("Not connected to Salesforce API")

        try:
            url = f"{self.base_url}/services/data/v52.0/query/"
            params = {"q": query}
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            records = response.json().get('records', [])
            log.info(f"Successfully retrieved records from Salesforce")
            return records
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve records from Salesforce")
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