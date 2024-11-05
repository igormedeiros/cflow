# File: power_bi_connector.py
import os
from typing import Optional, List, Any, Dict
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class PowerBIConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "PowerBIConnector",
            description: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            tenant_id: Optional[str] = None,
            group_id: Optional[str] = None,
            dataset_id: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the PowerBIConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Power BI integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.client_id = client_id or os.getenv('POWERBI_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('POWERBI_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.getenv('POWERBI_TENANT_ID')
        self.group_id = group_id or os.getenv('POWERBI_GROUP_ID')
        self.dataset_id = dataset_id or os.getenv('POWERBI_DATASET_ID')
        self.access_token = None
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        if not self.client_id or not self.client_secret or not self.tenant_id:
            raise ValueError("Power BI client ID, client secret, and tenant ID must be provided for PowerBIConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Power BI by retrieving an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._get_access_token()
            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to Power BI")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Power BI connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Power BI")
            raise

    def _get_access_token(self) -> None:
        """Retrieves an OAuth2 access token from Azure AD for Power BI API."""
        try:
            url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://analysis.windows.net/powerbi/api/.default'
            }
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            self.access_token = response.json().get('access_token')
            log.info("Successfully retrieved access token for Power BI")
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve access token for Power BI")
            raise

    def disconnect(self) -> None:
        """Disconnects from Power BI by invalidating the access token."""
        try:
            log.info("Disconnecting from Power BI")
            self.access_token = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Power BI disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if Power BI connection is successful by checking the access token."""
        if self.access_token:
            log.info("Power BI connection validated successfully")
            return True
        else:
            log.error("Power BI connection validation failed: No access token available")
            return False

    def push_data(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """Pushes data to the specified dataset in Power BI."""
        if not self.connected or not self.access_token:
            raise ConnectionError("Not connected to Power BI")

        try:
            url = f"{self.base_url}/groups/{self.group_id}/datasets/{self.dataset_id}/tables/{table_name}/rows"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            data = {
                'rows': rows
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            log.info(f"Successfully pushed data to Power BI table '{table_name}'")
        except Exception as e:
            self._handle_exception(e, f"Failed to push data to Power BI table '{table_name}'")
            raise

    def delete_rows(self, table_name: str) -> None:
        """Deletes all rows from the specified table in Power BI."""
        if not self.connected or not self.access_token:
            raise ConnectionError("Not connected to Power BI")

        try:
            url = f"{self.base_url}/groups/{self.group_id}/datasets/{self.dataset_id}/tables/{table_name}/rows"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            log.info(f"Successfully deleted rows from Power BI table '{table_name}'")
        except Exception as e:
            self._handle_exception(e, f"Failed to delete rows from Power BI table '{table_name}'")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Power BI connection."""
        return ['POWERBI_CLIENT_ID', 'POWERBI_CLIENT_SECRET', 'POWERBI_TENANT_ID', 'POWERBI_GROUP_ID', 'POWERBI_DATASET_ID']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False