# File: hotspot_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class HotspotConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "HotspotConnector",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the Hotspot Connector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Hotspot integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('HOTSPOT_API_KEY')
        self.base_url = f"https://api.hotspot.com/v1"

        if not self.api_key:
            raise ValueError("API Key must be provided for HotspotConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Hotspot by validating the API key."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Hotspot")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Hotspot connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Hotspot")
            raise

    def validate_connection(self) -> bool:
        """Validates if Hotspot connection is successful by making a test request."""
        try:
            url = f"{self.base_url}/test-connection"
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                log.info("Hotspot connection validated successfully")
                return True
            else:
                log.error(f"Hotspot connection validation failed with status code {response.status_code}")
                return False
        except Exception as e:
            self._handle_exception(e, "Hotspot connection validation failed")
            return False

    def disconnect(self) -> None:
        """Disconnects from Hotspot by invalidating the session."""
        try:
            log.info("Disconnecting from Hotspot")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Hotspot disconnection")
            raise

    def create_device(self, device_name: str, mac_address: str) -> Dict[str, Any]:
        """Creates a new device in Hotspot."""
        if not self.connected:
            raise ConnectionError("Not connected to Hotspot")

        try:
            url = f"{self.base_url}/devices"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                "name": device_name,
                "mac_address": mac_address
            }
            response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created device in Hotspot with name '{device_name}'")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to create device in Hotspot with name '{device_name}'")
            raise

    def get_device(self, device_id: str) -> Dict[str, Any]:
        """Fetches a device from Hotspot by device ID."""
        if not self.connected:
            raise ConnectionError("Not connected to Hotspot")

        try:
            url = f"{self.base_url}/devices/{device_id}"
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched device with ID '{device_id}' from Hotspot")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch device with ID '{device_id}' from Hotspot")
            raise

    def update_device(self, device_id: str, updates: Dict[str, Any]) -> None:
        """Updates a device in Hotspot by device ID."""
        if not self.connected:
            raise ConnectionError("Not connected to Hotspot")

        try:
            url = f"{self.base_url}/devices/{device_id}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.put(url, headers=headers, json=updates, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully updated device with ID '{device_id}' in Hotspot")
        except Exception as e:
            self._handle_exception(e, f"Failed to update device with ID '{device_id}' in Hotspot")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Hotspot connection."""
        return ['HOTSPOT_API_KEY']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False