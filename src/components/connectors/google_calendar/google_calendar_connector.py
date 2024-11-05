# File: google_calendar_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class GoogleCalendarConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "GoogleCalendarConnector",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the GoogleCalendarConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Google Calendar integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('GOOGLE_CALENDAR_API_KEY')
        self.client_id = client_id or os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('GOOGLE_CLIENT_SECRET')
        self.token_url = "https://oauth2.googleapis.com/token"
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.access_token = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with Google Calendar API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._get_access_token()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Google Calendar API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Google Calendar connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Google Calendar")
            raise

    def disconnect(self) -> None:
        """Disconnects from Google Calendar API."""
        try:
            log.info("Disconnecting from Google Calendar API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Google Calendar disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Google Calendar API."""
        try:
            if not self.access_token:
                return False
            url = f"{self.base_url}/users/me/calendarList"
            response = requests.get(url, headers=self._auth_headers(), timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Google Calendar connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['GOOGLE_CALENDAR_API_KEY', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']

    def _get_access_token(self) -> None:
        """Obtains an access token using client credentials."""
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
            response = requests.post(self.token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=self.timeout)
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            log.info("Successfully obtained access token for Google Calendar API")
        except Exception as e:
            self._handle_exception(e, "Failed to obtain access token for Google Calendar API")
            raise

    def _auth_headers(self) -> Dict[str, str]:
        """Returns headers with authorization for requests."""
        return {**self.headers, "Authorization": f"Bearer {self.access_token}"}

    def create_event(self, calendar_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an event in a specified Google Calendar."""
        if not self.connected:
            raise ConnectionError("Not connected to Google Calendar API")

        try:
            url = f"{self.base_url}/calendars/{calendar_id}/events"
            response = requests.post(url, json=event_data, headers=self._auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created event in calendar ID: {calendar_id}")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to create event in calendar ID: {calendar_id}")
            return {}

    def get_events(self, calendar_id: str) -> List[Dict[str, Any]]:
        """Gets a list of events from a specified Google Calendar."""
        if not self.connected:
            raise ConnectionError("Not connected to Google Calendar API")

        try:
            url = f"{self.base_url}/calendars/{calendar_id}/events"
            response = requests.get(url, headers=self._auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            events = response.json()
            log.info(f"Successfully retrieved events from calendar ID: {calendar_id}")
            return events.get('items', [])
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve events from calendar ID: {calendar_id}")
            return []

    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Deletes an event from a specified Google Calendar."""
        if not self.connected:
            raise ConnectionError("Not connected to Google Calendar API")

        try:
            url = f"{self.base_url}/calendars/{calendar_id}/events/{event_id}"
            response = requests.delete(url, headers=self._auth_headers(), timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully deleted event ID: {event_id} from calendar ID: {calendar_id}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to delete event ID: {event_id} from calendar ID: {calendar_id}")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False