# File: sharepoint_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SharePointConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SharePointConnector",
            description: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            tenant_id: Optional[str] = None,
            site_id: Optional[str] = None,
            access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SharePoint Connector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Microsoft SharePoint integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.client_id = client_id or os.getenv('SHAREPOINT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SHAREPOINT_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.getenv('SHAREPOINT_TENANT_ID')
        self.site_id = site_id or os.getenv('SHAREPOINT_SITE_ID')
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"

        if not self.client_id or not self.client_secret or not self.tenant_id or not self.site_id:
            raise ValueError("Client ID, Client Secret, Tenant ID, and Site ID must be provided for SharePointConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Microsoft SharePoint by retrieving an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._get_access_token()
            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Microsoft SharePoint")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Microsoft SharePoint connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Microsoft SharePoint")
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
            log.info("Successfully retrieved access token for Microsoft SharePoint")
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve access token for Microsoft SharePoint")
            raise

    def disconnect(self) -> None:
        """Disconnects from Microsoft SharePoint by invalidating the access token."""
        try:
            log.info("Disconnecting from Microsoft SharePoint")
            self.access_token = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Microsoft SharePoint disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if Microsoft SharePoint connection is successful by checking the access token."""
        if self.access_token:
            log.info("Microsoft SharePoint connection validated successfully")
            return True
        else:
            log.error("Microsoft SharePoint connection validation failed: No access token available")
            return False

    def get_list_items(self, list_id: str) -> Dict[str, Any]:
        """Fetches items from the specified SharePoint list."""
        if not self.connected or not self.access_token:
            raise ConnectionError("Not connected to Microsoft SharePoint")

        try:
            url = f"{self.base_url}/sites/{self.site_id}/lists/{list_id}/items"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched items from list '{list_id}' in SharePoint site '{self.site_id}'")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch items from list '{list_id}' in SharePoint site '{self.site_id}'")
            raise

    def upload_file(self, drive_id: str, file_path: str, file_name: str) -> None:
        """Uploads a file to the specified SharePoint document library."""
        if not self.connected or not self.access_token:
            raise ConnectionError("Not connected to Microsoft SharePoint")

        try:
            url = f"{self.base_url}/sites/{self.site_id}/drives/{drive_id}/root:/{file_name}:/content"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/octet-stream'
            }
            with open(file_path, 'rb') as file_data:
                response = requests.put(url, headers=headers, data=file_data, timeout=self.timeout)
                response.raise_for_status()
            log.info(f"Successfully uploaded file '{file_name}' to SharePoint drive '{drive_id}'")
        except Exception as e:
            self._handle_exception(e, f"Failed to upload file '{file_name}' to SharePoint drive '{drive_id}'")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Microsoft SharePoint connection."""
        return ['SHAREPOINT_CLIENT_ID', 'SHAREPOINT_CLIENT_SECRET', 'SHAREPOINT_TENANT_ID', 'SHAREPOINT_SITE_ID']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False