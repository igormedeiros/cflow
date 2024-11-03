# File: freshdesk_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class FreshdeskConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "FreshdeskConnector",
            description: Optional[str] = None,
            domain: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the Freshdesk Connector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Freshdesk integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.domain = domain or os.getenv('FRESHDESK_DOMAIN')
        self.api_key = api_key or os.getenv('FRESHDESK_API_KEY')
        self.base_url = f"https://{self.domain}.freshdesk.com/api/v2"

        if not self.domain or not self.api_key:
            raise ValueError("Domain and API Key must be provided for FreshdeskConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Freshdesk by validating the API key."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Freshdesk")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Freshdesk connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Freshdesk")
            raise

    def validate_connection(self) -> bool:
        """Validates if Freshdesk connection is successful by making a test request."""
        try:
            url = f"{self.base_url}/tickets"
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.get(url, auth=(self.api_key, 'X'), headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                log.info("Freshdesk connection validated successfully")
                return True
            else:
                log.error(f"Freshdesk connection validation failed with status code {response.status_code}")
                return False
        except Exception as e:
            self._handle_exception(e, "Freshdesk connection validation failed")
            return False

    def disconnect(self) -> None:
        """Disconnects from Freshdesk by invalidating the session."""
        try:
            log.info("Disconnecting from Freshdesk")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Freshdesk disconnection")
            raise

    def create_ticket(self, subject: str, description: str, email: str, priority: int, status: int) -> Dict[str, Any]:
        """Creates a ticket in Freshdesk."""
        if not self.connected:
            raise ConnectionError("Not connected to Freshdesk")

        try:
            url = f"{self.base_url}/tickets"
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                "subject": subject,
                "description": description,
                "email": email,
                "priority": priority,
                "status": status
            }
            response = requests.post(url, auth=(self.api_key, 'X'), headers=headers, json=data, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created ticket in Freshdesk with subject '{subject}'")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to create ticket in Freshdesk with subject '{subject}'")
            raise

    def get_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """Fetches a ticket from Freshdesk by ticket ID."""
        if not self.connected:
            raise ConnectionError("Not connected to Freshdesk")

        try:
            url = f"{self.base_url}/tickets/{ticket_id}"
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.get(url, auth=(self.api_key, 'X'), headers=headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched ticket with ID '{ticket_id}' from Freshdesk")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch ticket with ID '{ticket_id}' from Freshdesk")
            raise

    def update_ticket(self, ticket_id: int, updates: Dict[str, Any]) -> None:
        """Updates a ticket in Freshdesk by ticket ID."""
        if not self.connected:
            raise ConnectionError("Not connected to Freshdesk")

        try:
            url = f"{self.base_url}/tickets/{ticket_id}"
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.put(url, auth=(self.api_key, 'X'), headers=headers, json=updates, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully updated ticket with ID '{ticket_id}' in Freshdesk")
        except Exception as e:
            self._handle_exception(e, f"Failed to update ticket with ID '{ticket_id}' in Freshdesk")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Freshdesk connection."""
        return ['FRESHDESK_DOMAIN', 'FRESHDESK_API_KEY']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False