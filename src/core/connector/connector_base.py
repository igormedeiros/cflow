import re
import time
from abc import ABC, abstractmethod
from typing import Any

import requests

from core.config import ConnectorConfig
from core.connector.connector_protocol import ConnectorProtocol
from core.logger import log
from core.utils import load_environment_variables


# Custom Errors
class ConnectionFailedError(Exception):
    """
    Raised when a connection attempt fails.
    """

    def __init__(self, message="Connection failed"):
        super().__init__(message)


class InvalidCredentialsError(Exception):
    """
    Raised when credentials are invalid or missing.
    """

    def __init__(self, message="Invalid or missing credentials"):
        super().__init__(message)


class NotifiableConnector(ABC):
    """
    Interface for connectors that can send notifications.
    """

    @abstractmethod
    def notify(self, message: str = None) -> bool:
        """
        Send a notification through the connector.

        Args:
            message: Optional message to send. If None, uses a default message.

        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        pass


class ConnectorBase(ABC, ConnectorProtocol):
    def __init__(self, name, description=None, retry_attempts=3, timeout=30, enable_retry=True):
        """
        Initializes the base connector with a name, optional description, retry attempts, and timeout.
        :param name: The name of the connector.
        :param description: Optional description for the connector.
        :param retry_attempts: Number of retry attempts for failed connections.
        :param timeout: Timeout duration for the connection in seconds.
        :param enable_retry: Toggle to enable or disable retry mechanism.
        """
        self.validate_attribute('name', name)
        self.validate_attribute('retry_attempts', retry_attempts, int)
        self.validate_attribute('timeout', timeout, int)
        self.name = name
        self.description = description
        self.retry_attempts = retry_attempts
        self.timeout = timeout
        self.enable_retry = enable_retry
        self.connected = False
        self.session = requests.Session()

    @abstractmethod
    def connect(self, **kwargs) -> None:
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()
            time.sleep(self.timeout / 10)
            log.info(ConnectorConfig.CONNECTING_MESSAGE.format(self.name))
            self.connected = True
            self.post_connect_hook()
        except ValueError as ve:
            self._handle_exception(ve, "ValueError encountered during connection")
            raise InvalidCredentialsError(str(ve)) from ve
        except Exception as e:
            self._handle_exception(e, "Unexpected error during connection")
            raise ConnectionFailedError(str(e)) from e

    def _load_credentials(self) -> None:
        """Loads environment variables required for the connector."""
        self.credentials = load_environment_variables(self.get_env_keys())

    def _validate_credentials(self) -> None:
        """Validates if all required credentials are available and structurally correct."""
        for key, value in self.credentials.items():
            if value is None:
                self._handle_exception(
                    ValueError(f"Missing required credential: '{key}'"),
                    "Missing credentials during validation"
                )
                raise InvalidCredentialsError(f"Missing required credential: '{key}' for connection.")
            if key == "API_KEY" and (not re.match(r"^[A-Za-z0-9]{32,}$", value)):
                self._handle_exception(
                    ValueError(f"Invalid credential format for '{key}'"),
                    "Credential validation failed"
                )
                raise InvalidCredentialsError(
                    f"Invalid credential format for '{key}': must be alphanumeric and at least 32 characters long."
                )

    def validate_parameters(self, params: dict) -> None:
        """Validates the parameters passed to the connect method."""
        for key, value in params.items():
            if value is None:
                self._handle_exception(
                    ValueError(f"Parameter '{key}' is required but not provided."),
                    "Parameter validation failed"
                )
                raise ValueError(f"Parameter '{key}' is required but not provided for connector '{self.name}'.")

    def validate_attribute(self, attribute_name: str, value: Any, expected_type: type = None) -> None:
        """Validates the attributes of the connector."""
        if value is None:
            self._handle_exception(
                ValueError(f"Attribute '{attribute_name}' is required but not provided."),
                "Attribute validation failed"
            )
            raise ValueError(f"Attribute '{attribute_name}' is required but not provided for connector '{self.name}'.")
        if expected_type and not isinstance(value, expected_type):
            self._handle_exception(
                TypeError(f"Attribute '{attribute_name}' must be of type {expected_type.__name__}"),
                "Attribute validation failed"
            )
            raise TypeError(
                f"Attribute '{attribute_name}' must be of type {expected_type.__name__}, but got {type(value).__name__} for connector '{self.name}'."
            )

    def _handle_exception(self, exception: Exception, context: str) -> None:
        """Handles exceptions by logging them consistently."""
        log.error(f"{context}: {exception}. Context: Connector '{self.name}'.")

    def _log_attempts(self, attempt_number: int) -> None:
        """Logs the details of each retry attempt."""
        log.info(ConnectorConfig.RETRY_ATTEMPT_MESSAGE.format(attempt_number, self.name))

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnects from the service."""
        try:
            log.info(ConnectorConfig.DISCONNECTING_MESSAGE.format(self.name))
            self.session.close()
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Unexpected error during disconnection")
            self.connected = False
            raise

    @abstractmethod
    def validate_connection(self) -> bool:
        """Validates if the connection is active and working."""
        try:
            log.info(ConnectorConfig.VALIDATING_CONNECTION_MESSAGE.format(self.name))
            return True
        except Exception as e:
            self._handle_exception(e, "Error during connection validation")
            raise

    @abstractmethod
    def get_env_keys(self) -> list:
        """Returns list of required environment variable keys."""
        pass

    def get_info(self) -> dict:
        """Returns information about the connector."""
        return {
            "name": self.name,
            "description": self.description if self.description else ConnectorConfig.NO_DESCRIPTION_PROVIDED,
            "retry_attempts": self.retry_attempts,
            "timeout": self.timeout,
            "enable_retry": self.enable_retry,
            "is_connected": self.connected
        }

    def pre_connect_hook(self, kwargs):
        """Hook method executed before connection."""
        pass

    def post_connect_hook(self):
        """Hook method executed after successful connection."""
        pass