# File: netflix_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class NetflixConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "NetflixConnector",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the Netflix Connector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Netflix API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('NETFLIX_API_KEY')
        self.base_url = "https://api.netflix.com/v1"

        if not self.api_key:
            raise ValueError("API Key must be provided for NetflixConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Netflix by validating the API key."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Netflix API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Netflix API connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Netflix API")
            raise

    def validate_connection(self) -> bool:
        """Validates if Netflix API connection is successful by making a test request."""
        try:
            url = f"{self.base_url}/test-connection"
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                log.info("Netflix API connection validated successfully")
                return True
            else:
                log.error(f"Netflix API connection validation failed with status code {response.status_code}")
                return False
        except Exception as e:
            self._handle_exception(e, "Netflix API connection validation failed")
            return False

    def disconnect(self) -> None:
        """Disconnects from Netflix API by invalidating the session."""
        try:
            log.info("Disconnecting from Netflix API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Netflix API disconnection")
            raise

    def search_titles(self, query: str) -> List[Dict[str, Any]]:
        """Searches for titles on Netflix based on a query."""
        if not self.connected:
            raise ConnectionError("Not connected to Netflix API")

        try:
            url = f"{self.base_url}/search/titles"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            params = {
                'query': query
            }
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched search results for query '{query}' from Netflix API")
            return response.json().get('results', [])
        except Exception as e:
            self._handle_exception(e, f"Failed to search titles with query '{query}' from Netflix API")
            raise

    def get_title_details(self, title_id: str) -> Dict[str, Any]:
        """Fetches details of a specific title from Netflix by title ID."""
        if not self.connected:
            raise ConnectionError("Not connected to Netflix API")

        try:
            url = f"{self.base_url}/titles/{title_id}"
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched details for title ID '{title_id}' from Netflix API")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch details for title ID '{title_id}' from Netflix API")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Netflix API connection."""
        return ['NETFLIX_API_KEY']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False
