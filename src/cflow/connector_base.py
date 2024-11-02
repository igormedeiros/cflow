from logger import log
from abc import ABC, abstractmethod
from connector_protocol import ConnectorProtocol
from config import ConnectorConfig
from environment_loader import load_environment_variables
import requests
import os
import time
import random
import re


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


class ConnectorBase(ABC, ConnectorProtocol):
    def __init__(self, name, description=None, retry_attempts=3, timeout=30, enable_retry=True):
        """
        Initializes the base connector with a name, optional description, retry attempts, and timeout.
        :param name: The name of the connector.
        :param description: Optional description for the connector.
        :param retry_attempts: Number of retry attempts for failed connections.
        :param timeout: Timeout duration for the connection in seconds.
        :param enable_retry: Toggle to enable or disable retry mechanism.

        Example:
        ```python
        connector = ConnectorBase(name="MyConnector", retry_attempts=5, timeout=60)
        ```
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
        self.session = requests.Session()  # Using a session for better performance in multiple requests

    @abstractmethod
    def connect(self, **kwargs) -> None:
        """
        Abstract method to establish a connection to the desired endpoint.
        Must be implemented by all subclasses.

        Validates the provided parameters before establishing the connection.
        :param kwargs: Additional parameters required for connection.

        Example:
        ```python
        connector = MyConnector()
        connector.connect(param1="value1")
        ```
        """
        try:
            # Hook before connecting
            self.pre_connect_hook(kwargs)

            # Validate parameters
            self.validate_parameters(kwargs)

            # Load credentials and validate
            self._load_credentials()
            self._validate_credentials()

            # Set connection timeout
            time.sleep(self.timeout / 10)  # Simulate the timeout in the connection

            log.info(ConnectorConfig.CONNECTING_MESSAGE.format(self.name))
            self.connected = True

            # Hook after successful connection
            self.post_connect_hook()
        except ValueError as ve:
            self._handle_exception(ve, "ValueError encountered during connection")
            raise InvalidCredentialsError(str(ve)) from ve
        except Exception as e:
            self._handle_exception(e, "Unexpected error during connection")
            raise ConnectionFailedError(str(e)) from e

    def _load_credentials(self) -> None:
        """
        Loads environment variables required for the connector from a decoupled layer.

        Example:
        ```python
        connector = MyConnector()
        connector._load_credentials()
        ```
        """
        self.credentials = load_environment_variables(self.get_env_keys())

    def _validate_credentials(self) -> None:
        """
        Validates if all required credentials are available and structurally correct.

        Example:
        ```python
        connector = MyConnector()
        connector._validate_credentials()
        ```
        """
        for key, value in self.credentials.items():
            if value is None:
                self._handle_exception(ValueError(f"Missing required credential: '{key}'"),
                                       "Missing credentials during validation")
                raise InvalidCredentialsError(f"Missing required credential: '{key}' for connection.")
            # Example of structural validation: API key must be alphanumeric and at least 32 characters
            if key == "API_KEY" and (not re.match(r"^[A-Za-z0-9]{32,}$", value)):
                self._handle_exception(ValueError(f"Invalid credential format for '{key}'"),
                                       "Credential validation failed")
                raise InvalidCredentialsError(
                    f"Invalid credential format for '{key}': must be alphanumeric and at least 32 characters long.")

    def validate_parameters(self, params: dict) -> None:
        """
        Validates the parameters passed to the connect method.
        :param params: Dictionary of parameters to validate.

        Example:
        ```python
        connector = MyConnector()
        connector.validate_parameters(params={"param1": "value1"})
        ```
        """
        for key, value in params.items():
            if value is None:
                self._handle_exception(ValueError(f"Parameter '{key}' is required but not provided."),
                                       "Parameter validation failed")
                raise ValueError(f"Parameter '{key}' is required but not provided for connector '{self.name}'.")

    def validate_attribute(self, attribute_name: str, value: Any, expected_type: type = None) -> None:
        """
        Validates the attributes of the connector.
        :param attribute_name: Name of the attribute to validate.
        :param value: The value of the attribute.
        :param expected_type: The expected type of the attribute (optional).

        Example:
        ```python
        connector = MyConnector()
        connector.validate_attribute(attribute_name="timeout", value=30, expected_type=int)
        ```
        """
        if value is None:
            self._handle_exception(ValueError(f"Attribute '{attribute_name}' is required but not provided."),
                                   "Attribute validation failed")
            raise ValueError(f"Attribute '{attribute_name}' is required but not provided for connector '{self.name}'.")
        if expected_type and not isinstance(value, expected_type):
            self._handle_exception(TypeError(f"Attribute '{attribute_name}' must be of type {expected_type.__name__}"),
                                   "Attribute validation failed")
            raise TypeError(
                f"Attribute '{attribute_name}' must be of type {expected_type.__name__}, but got {type(value).__name__} for connector '{self.name}'.")

    def _handle_exception(self, exception: Exception, context: str) -> None:
        """
        Handles exceptions by logging them consistently.
        :param exception: The exception that occurred.
        :param context: A description of the context in which the exception occurred.

        Example:
        ```python
        connector = MyConnector()
        try:
            connector.connect()
        except Exception as e:
            connector._handle_exception(e, "Error during custom operation")
        ```
        """
        log.error(f"{context}: {exception}. Context: Connector '{self.name}'.")

    def _log_attempts(self, attempt_number: int) -> None:
        """
        Logs the details of each retry attempt.
        :param attempt_number: The number of the current attempt.

        Example:
        ```python
        connector = MyConnector()
        connector._log_attempts(attempt_number=1)
        ```
        """
        log.info(ConnectorConfig.RETRY_ATTEMPT_MESSAGE.format(attempt_number, self.name))

    @abstractmethod
    def disconnect(self) -> None:
        """
        Abstract method to close the connection if applicable.
        Must be implemented by all subclasses.

        Example:
        ```python
        connector = MyConnector()
        connector.disconnect()
        ```
        """
        try:
            log.info(ConnectorConfig.DISCONNECTING_MESSAGE.format(self.name))
            self.session.close()  # Close the session to release resources
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Unexpected error during disconnection")
            # Ensure the connected state is False even if an error occurs during disconnection
            self.connected = False
            raise

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Abstract method to validate the connection.
        Must be implemented by all subclasses.
        :return: Boolean indicating if the connection is valid.

        Example:
        ```python
        connector = MyConnector()
        valid = connector.validate_connection()
        print(valid)
        ```
        """
        try:
            log.info(ConnectorConfig.VALIDATING_CONNECTION_MESSAGE.format(self.name))
            return True
        except Exception as e:
            self._handle_exception(e, "Error during connection validation")
            raise

    @abstractmethod
    def get_env_keys(self) -> list:
        """
        Abstract method to provide a list of environment variable keys for credentials.
        Must be implemented by all subclasses.
        :return: List of environment variable keys required for the connection.

        Example:
        ```python
        connector = MyConnector()
        keys = connector.get_env_keys()
        print(keys)
        ```
        """
        pass

    def get_info(self) -> dict:
        """
        Provides information about the connector.
        :return: Dictionary containing the name, description, retry attempts, timeout, retry status, and connection status.

        Example:
        ```python
        connector = MyConnector()
        info = connector.get_info()
        print(info)
        ```
        """
        return {
            "name": self.name,
            "description": self.description if self.description else ConnectorConfig.NO_DESCRIPTION_PROVIDED,
            "retry_attempts": self.retry_attempts,
            "timeout": self.timeout,
            "enable_retry": self.enable_retry,
            "is_connected": self.connected
        }