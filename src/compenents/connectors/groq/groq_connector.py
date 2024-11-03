# File: groq_connector.py
import os
import requests
from typing import Optional, List, Dict, Any
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class GroqConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "GroqConnector",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the GroqConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Groq API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def connect(self, **kwargs) -> None:
        """Establishes connection with Groq API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Groq API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Groq connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Groq API")
            raise

    def disconnect(self) -> None:
        """Disconnects from Groq API."""
        try:
            log.info("Disconnecting from Groq API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Groq disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Groq API."""
        try:
            if not self.api_key:
                log.error("Groq API key is not provided.")
                return False
            # Perform a simple API request to validate the connection
            response = requests.get(f"{self.base_url}/status", headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Groq connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['GROQ_API_KEY']

    def execute_query(self, query: str) -> Dict[str, Any]:
        """Executes a query using the Groq API."""
        if not self.connected:
            raise ConnectionError("Not connected to Groq API")

        try:
            payload = {"query": query}
            response = requests.post(f"{self.base_url}/query", headers=self.headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            log.info("Successfully executed query using Groq API")
            return response.json()
        except Exception as e:
            self._handle_exception(e, "Failed to execute query using Groq API")
            return {}

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False