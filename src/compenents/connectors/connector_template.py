import os
from typing import Optional, List, Any

from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class ConnectorTemplate(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "ConnectorTemplate",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            endpoint_url: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the ConnectorTemplate instance.
        """
        super().__init__(
            name=name,
            description=description or "Generic Connector Template",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('API_KEY')
        self.endpoint_url = endpoint_url or os.getenv('ENDPOINT_URL')
        self.base_url = self.endpoint_url if self.endpoint_url else None
        self._last_data = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with the endpoint."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to endpoint at: {self.endpoint_url}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to endpoint")
            raise

    def disconnect(self) -> None:
        """Disconnects from the endpoint."""
        try:
            log.info(f"Disconnecting from endpoint at: {self.endpoint_url}")
            self.connected = False
            self.session.close()
        except Exception as e:
            self._handle_exception(e, "Error during endpoint disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to the endpoint."""
        try:
            if not self.api_key or not self.endpoint_url:
                return False

            response = self.session.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['API_KEY', 'ENDPOINT_URL']

    def send_data(self, data: Any) -> bool:
        """Processes and sends data through the endpoint."""
        if not self.connected:
            raise ConnectionError("Not connected to endpoint")

        try:
            url = f"{self.base_url}/sendData"
            payload = {
                "api_key": self.api_key,
                "data": data
            }

            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send data to endpoint: {str(e)}")
            return False

    def process_data(self, data: Any) -> str:
        """Processes data before sending it to the endpoint."""
        if isinstance(data, dict):
            return "\n".join([f"{k}: {v}" for k, v in data.items()])
        elif isinstance(data, (list, tuple)):
            return "\n".join(map(str, data))
        return str(data)

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            return self.send_data(message or default_message)
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False
