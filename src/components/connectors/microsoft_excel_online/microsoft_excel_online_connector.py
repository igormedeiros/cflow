# File: microsoft_excel_online_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class MicrosoftExcelOnlineConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "MicrosoftExcelOnlineConnector",
            description: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            tenant_id: Optional[str] = None,
            access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the Microsoft Excel Online Connector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Microsoft Excel Online integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.client_id = client_id or os.getenv('EXCEL_ONLINE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('EXCEL_ONLINE_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.getenv('EXCEL_ONLINE_TENANT_ID')
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"

        if not self.client_id or not self.client_secret or not self.tenant_id:
            raise ValueError("Client ID, Client Secret, and Tenant ID must be provided for MicrosoftExcelOnlineConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Microsoft Excel Online by retrieving an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._get_access_token()
            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Microsoft Excel Online")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Microsoft Excel Online connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Microsoft Excel Online")
            raise

    def _get_access_token(self) -> None:
        """Retrieves an OAuth2 access token from Microsoft Identity Platform."""
        try:
            url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default'
            }
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            self.access_token = response.json().get('access_token')
            log.info("Successfully retrieved access token for Microsoft Excel Online")
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve access token for Microsoft Excel Online")
            raise

    def disconnect(self) -> None:
        """Disconnects from Microsoft Excel Online by invalidating the access token."""
        try:
            log.info("Disconnecting from Microsoft Excel Online")
            self.access_token = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Microsoft Excel Online disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if Microsoft Excel Online connection is successful by checking the access token."""
        if self.access_token:
            log.info("Microsoft Excel Online connection validated successfully")
            return True
        else:
            log.error("Microsoft Excel Online connection validation failed: No access token available")
            return False

    def get_worksheet_data(self, workbook_id: str, worksheet_name: str) -> Dict[str, Any]:
        """Fetches data from the specified worksheet in an Excel Online workbook."""
        if not self.connected or not self.access_token:
            raise ConnectionError("Not connected to Microsoft Excel Online")

        try:
            url = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/range"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched data from worksheet '{worksheet_name}' in workbook '{workbook_id}'")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch data from worksheet '{worksheet_name}' in workbook '{workbook_id}'")
            raise

    def update_worksheet_data(self, workbook_id: str, worksheet_name: str, range_address: str, values: List[List[Any]]) -> None:
        """Updates data in the specified range of a worksheet in an Excel Online workbook."""
        if not self.connected or not self.access_token:
            raise ConnectionError("Not connected to Microsoft Excel Online")

        try:
            url = f"{self.base_url}/me/drive/items/{workbook_id}/workbook/worksheets/{worksheet_name}/range(address='{range_address}')"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                "values": values
            }
            response = requests.patch(url, headers=headers, json=data, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully updated data in worksheet '{worksheet_name}' at range '{range_address}' in workbook '{workbook_id}'")
        except Exception as e:
            self._handle_exception(e, f"Failed to update data in worksheet '{worksheet_name}' at range '{range_address}' in workbook '{workbook_id}'")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Microsoft Excel Online connection."""
        return ['EXCEL_ONLINE_CLIENT_ID', 'EXCEL_ONLINE_CLIENT_SECRET', 'EXCEL_ONLINE_TENANT_ID']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False