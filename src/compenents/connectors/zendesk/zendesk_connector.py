# File: zendesk_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class ZendeskConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "ZendeskConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            email: Optional[str] = None,
            api_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the ZendeskConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Zendesk integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('ZENDESK_BASE_URL')
        self.email = email or os.getenv('ZENDESK_EMAIL')
        self.api_token = api_token or os.getenv('ZENDESK_API_TOKEN')
        self.headers = {
            "Content-Type": "application/json"
        }
        self.auth = (f"{self.email}/token", self.api_token)

    def connect(self, **kwargs) -> None:
        """Establishes connection with Zendesk API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Zendesk API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Zendesk connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Zendesk")
            raise

    def disconnect(self) -> None:
        """Disconnects from Zendesk API."""
        try:
            log.info("Disconnecting from Zendesk API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Zendesk disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Zendesk API."""
        try:
            if not self.base_url or not self.email or not self.api_token:
                return False
            url = f"{self.base_url}/api/v2/tickets.json"
            response = requests.get(url, auth=self.auth, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Zendesk connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['ZENDESK_BASE_URL', 'ZENDESK_EMAIL', 'ZENDESK_API_TOKEN']

    def create_ticket(self, ticket_data: Dict[str, Any]) -> bool:
        """Creates a new ticket in Zendesk."""
        if not self.connected:
            raise ConnectionError("Not connected to Zendesk API")

        try:
            url = f"{self.base_url}/api/v2/tickets.json"
            response = requests.post(url, json={"ticket": ticket_data}, auth=self.auth, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully created ticket in Zendesk")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create ticket in Zendesk")
            return False

    def get_tickets(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Gets tickets from Zendesk based on provided filters."""
        if not self.connected:
            raise ConnectionError("Not connected to Zendesk API")

        try:
            url = f"{self.base_url}/api/v2/tickets.json"
            response = requests.get(url, auth=self.auth, headers=self.headers, params=filters, timeout=self.timeout)
            response.raise_for_status()
            tickets = response.json().get('tickets', [])
            log.info("Successfully retrieved tickets from Zendesk")
            return tickets
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve tickets from Zendesk")
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