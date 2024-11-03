# File: sympla_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class SymplaConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SymplaConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SymplaConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Sympla integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('SYMPLA_BASE_URL', 'https://api.sympla.com.br')
        self.access_token = access_token or os.getenv('SYMPLA_ACCESS_TOKEN')
        self.headers = {
            "Content-Type": "application/json",
            "s_token": self.access_token
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Sympla API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Sympla API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Sympla connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Sympla")
            raise

    def disconnect(self) -> None:
        """Disconnects from Sympla API."""
        try:
            log.info("Disconnecting from Sympla API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Sympla disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Sympla API."""
        try:
            if not self.base_url or not self.access_token:
                return False
            url = f"{self.base_url}/public/v3/events"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Sympla connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SYMPLA_BASE_URL', 'SYMPLA_ACCESS_TOKEN']

    def get_events(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Gets events data from Sympla based on provided filters."""
        if not self.connected:
            raise ConnectionError("Not connected to Sympla API")

        try:
            url = f"{self.base_url}/public/v3/events"
            response = requests.get(url, headers=self.headers, params=filters, timeout=self.timeout)
            response.raise_for_status()
            events = response.json().get('data', [])
            log.info("Successfully retrieved events from Sympla")
            return events
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve events from Sympla")
            return []

    def get_event_details(self, event_id: str) -> Dict[str, Any]:
        """Gets event details by event ID from Sympla."""
        if not self.connected:
            raise ConnectionError("Not connected to Sympla API")

        try:
            url = f"{self.base_url}/public/v3/events/{event_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            event_details = response.json()
            log.info(f"Successfully retrieved event details for ID: {event_id}")
            return event_details
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve event details for ID: {event_id}")
            return {}

    def get_participants(self, event_id: str) -> List[Dict[str, Any]]:
        """Gets participants for a specific event by event ID from Sympla."""
        if not self.connected:
            raise ConnectionError("Not connected to Sympla API")

        try:
            url = f"{self.base_url}/public/v3/events/{event_id}/participants"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            participants = response.json().get('data', [])
            log.info(f"Successfully retrieved participants for event ID: {event_id}")
            return participants
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve participants for event ID: {event_id}")
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