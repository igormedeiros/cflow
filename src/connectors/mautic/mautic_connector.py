# File: mautic_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class MauticConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "MauticConnector",
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
        Initializes the MauticConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Mautic integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('MAUTIC_BASE_URL')
        self.client_id = client_id or os.getenv('MAUTIC_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('MAUTIC_CLIENT_SECRET')
        self.username = username or os.getenv('MAUTIC_USERNAME')
        self.password = password or os.getenv('MAUTIC_PASSWORD')
        self.access_token = None
        self.headers = {
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Mautic API and obtains an access token."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Mautic API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Mautic connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Mautic")
            raise

    def disconnect(self) -> None:
        """Disconnects from Mautic API."""
        try:
            log.info("Disconnecting from Mautic API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Mautic disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Mautic API by obtaining an access token."""
        try:
            if not self.base_url or not self.username or not self.password or not self.client_id or not self.client_secret:
                return False
            url = f"{self.base_url}/oauth/v2/token"
            data = {
                "grant_type": "password",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.username,
                "password": self.password
            }
            response = requests.post(url, data=data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            self.access_token = response.json().get('access_token')
            self.headers["Authorization"] = f"Bearer {self.access_token}"
            return True
        except Exception as e:
            self._handle_exception(e, "Mautic connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['MAUTIC_BASE_URL', 'MAUTIC_CLIENT_ID', 'MAUTIC_CLIENT_SECRET', 'MAUTIC_USERNAME', 'MAUTIC_PASSWORD']

    def create_contact(self, contact_data: Dict[str, Any]) -> bool:
        """Creates a new contact in Mautic."""
        if not self.connected:
            raise ConnectionError("Not connected to Mautic API")

        try:
            url = f"{self.base_url}/api/contacts/new"
            response = requests.post(url, json=contact_data, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully created contact in Mautic")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create contact in Mautic")
            return False

    def get_contacts(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Gets contacts from Mautic based on provided filters."""
        if not self.connected:
            raise ConnectionError("Not connected to Mautic API")

        try:
            url = f"{self.base_url}/api/contacts"
            response = requests.get(url, headers=self.headers, params=filters, timeout=self.timeout)
            response.raise_for_status()
            contacts = response.json().get('contacts', [])
            log.info("Successfully retrieved contacts from Mautic")
            return contacts
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve contacts from Mautic")
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