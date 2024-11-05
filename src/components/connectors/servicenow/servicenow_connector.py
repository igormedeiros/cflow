# File: servicenow_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class ServiceNowConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "ServiceNowConnector",
            description: Optional[str] = None,
            instance_url: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the ServiceNowConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for ServiceNow integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.instance_url = instance_url or os.getenv('SERVICENOW_INSTANCE_URL')
        self.username = username or os.getenv('SERVICENOW_USERNAME')
        self.password = password or os.getenv('SERVICENOW_PASSWORD')
        self.base_url = f"{self.instance_url}/api/now"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with ServiceNow API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to ServiceNow API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate ServiceNow connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to ServiceNow")
            raise

    def disconnect(self) -> None:
        """Disconnects from ServiceNow API."""
        try:
            log.info("Disconnecting from ServiceNow API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during ServiceNow disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to ServiceNow API."""
        try:
            if not self.instance_url or not self.username or not self.password:
                return False
            url = f"{self.base_url}/table/incident?sysparm_limit=1"
            response = requests.get(url, auth=(self.username, self.password), headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "ServiceNow connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SERVICENOW_INSTANCE_URL', 'SERVICENOW_USERNAME', 'SERVICENOW_PASSWORD']

    def create_incident(self, incident_data: Dict[str, Any]) -> bool:
        """Creates a new incident in ServiceNow."""
        if not self.connected:
            raise ConnectionError("Not connected to ServiceNow API")

        try:
            url = f"{self.base_url}/table/incident"
            response = requests.post(url, json=incident_data, auth=(self.username, self.password), headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully created incident in ServiceNow")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create incident in ServiceNow")
            return False

    def get_incidents(self, query_params: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Gets incidents from ServiceNow based on the provided query parameters."""
        if not self.connected:
            raise ConnectionError("Not connected to ServiceNow API")

        try:
            url = f"{self.base_url}/table/incident"
            response = requests.get(url, params=query_params, auth=(self.username, self.password), headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            incidents = response.json().get('result', [])
            log.info("Successfully retrieved incidents from ServiceNow")
            return incidents
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve incidents from ServiceNow")
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
