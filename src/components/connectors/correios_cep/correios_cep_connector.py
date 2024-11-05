# File: correios_cep_connector.py
import requests
from typing import Optional, List, Dict, Any
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class CorreiosCEPConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "CorreiosCEPConnector",
            description: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the CorreiosCEPConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Correios CEP API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = "https://viacep.com.br/ws"

    def connect(self, **kwargs) -> None:
        """Establishes connection with Correios CEP API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Correios CEP API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Correios CEP connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Correios CEP API")
            raise

    def disconnect(self) -> None:
        """Disconnects from Correios CEP API."""
        try:
            log.info("Disconnecting from Correios CEP API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Correios CEP disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Correios CEP API."""
        try:
            # The ViaCEP API is open and does not require credentials, perform a simple test request
            response = requests.get(f"{self.base_url}/01001000/json/", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Correios CEP connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return []  # No environment keys are needed for ViaCEP

    def get_address_by_cep(self, cep: str) -> Dict[str, Any]:
        """Fetches address information from Correios API using a given CEP (postal code)."""
        if not self.connected:
            raise ConnectionError("Not connected to Correios CEP API")

        try:
            response = requests.get(f"{self.base_url}/{cep}/json/", timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully fetched address information for CEP {cep}")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch address information for CEP {cep}")
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