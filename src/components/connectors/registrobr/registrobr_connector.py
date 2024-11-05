# File: registrobr_connector.py
from typing import Optional, List, Dict, Any

import requests

from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class RegistroBrConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "RegistroBrConnector",
            description: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the RegistroBrConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Registro.br WHOIS API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = "https://rdap.registro.br/domain/"

    def connect(self, **kwargs) -> None:
        """Establishes connection with Registro.br API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Registro.br API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Registro.br connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Registro.br API")
            raise

    def disconnect(self) -> None:
        """Disconnects from Registro.br API."""
        try:
            log.info("Disconnecting from Registro.br API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Registro.br disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Registro.br API."""
        try:
            # Perform a simple request to validate the connection
            response = requests.get(f"{self.base_url}example.com.br", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Registro.br connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return []  # No environment keys are needed for Registro.br API

    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Fetches WHOIS information for a given domain from Registro.br API."""
        if not self.connected:
            raise ConnectionError("Not connected to Registro.br API")

        try:
            response = requests.get(f"{self.base_url}{domain}", timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched domain information for {domain}")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch domain information for {domain}")
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