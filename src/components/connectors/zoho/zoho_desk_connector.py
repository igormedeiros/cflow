# File: zoho_desk_connector.py
import os
import requests
from typing import Optional, Dict, Any
from core.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log

class ZohoDeskConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "ZohoDeskConnector",
            description: Optional[str] = None,
            organization_id: Optional[str] = None,
            access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        super().__init__(
            name=name,
            description=description or "Connector for Zoho Desk integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.organization_id = organization_id or os.getenv('ZOHO_DESK_ORGANIZATION_ID')
        self.access_token = access_token or os.getenv('ZOHO_DESK_ACCESS_TOKEN')
        self.base_url = f"https://desk.zoho.com/api/v1"
        self.headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "orgId": self.organization_id,
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Zoho Desk API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Zoho Desk connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Zoho Desk")
            raise

    def disconnect(self) -> None:
        try:
            log.info("Disconnecting from Zoho Desk API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Zoho Desk disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Zoho Desk by retrieving basic account information."""
        try:
            url = f"{self.base_url}/tickets"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Zoho Desk connection validation failed")
            return False

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Fetches details of a specific ticket by ID."""
        if not self.connected:
            raise ConnectionError("Not connected to Zoho Desk API")

        try:
            url = f"{self.base_url}/tickets/{ticket_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully retrieved ticket with ID: {ticket_id}")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve ticket with ID: {ticket_id}")
            return None

    def search_tickets(self, search_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Searches for tickets matching specific parameters."""
        if not self.connected:
            raise ConnectionError("Not connected to Zoho Desk API")

        try:
            url = f"{self.base_url}/tickets/search"
            response = requests.get(url, headers=self.headers, params=search_params, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully retrieved tickets based on search criteria")
            return response.json()
        except Exception as e:
            self._handle_exception(e, "Failed to search tickets in Zoho Desk")
            return None

    def notify(self, message: str = None) -> bool:
        """Simple notifier for integration status updates."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False
