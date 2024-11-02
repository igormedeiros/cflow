# Arquivo: src/connectors/rest_connector/rest_connector.py

from src.cflow.connector_base import ConnectorBase
import requests
from logger import log


class RestConnector(ConnectorBase):
    def __init__(self, name="RestConnector", description=None, base_url=None, endpoint=None, headers=None,
                 retry_attempts=3, timeout=30, enable_retry=True):
        """
        Initializes the RestConnector instance with specific parameters.

        :param name: Name of the connector.
        :param description: Optional description of the connector.
        :param base_url: Base URL of the REST API.
        :param endpoint: Endpoint to be used for the REST API requests.
        :param headers: Optional headers to be used for the REST API requests.
        :param retry_attempts: Number of times to retry the connection in case of failure.
        :param timeout: Timeout value for the connection.
        :param enable_retry: Flag to enable or disable retry attempts.
        """
        super().__init__(name, description if description else "Sends POST requests to a REST API", retry_attempts,
                         timeout, enable_retry)
        self.base_url = base_url
        self.endpoint = endpoint
        self.url = f"{self.base_url}/{self.endpoint}" if self.base_url and self.endpoint else None
        self.headers = headers if headers else {}
        self.setup_connector()

    def setup_connector(self):
        """
        Initial setup of the REST connector.
        Defines specific variables and additional settings required for the proper functioning of the connector.
        """
        log.info(f"Setting up REST Connector with name: {self.name}")
        if not self.base_url or not self.endpoint:
            log.error("Base URL or endpoint is not provided.")
            raise ValueError("Base URL and endpoint must be provided for RestConnector.")

    def connect(self, **kwargs) -> None:
        """
        Establishes a connection by setting up the REST API endpoint.

        :param kwargs: Additional parameters required for connection.
        """
        log.info(f"Ready to make REST requests to: {self.url}")
        # Connection setup logic for REST API
        self.is_connected = True

    def disconnect(self) -> None:
        """
        Disconnects from the REST API.
        Sets the internal state to disconnected.
        """
        log.info(f"Disconnecting from REST API at: {self.url}")
        self.is_connected = False

    def validate_connection(self) -> bool:
        """
        Validates if the REST API connection is still valid by performing a health check or similar operation.

        :return: Boolean indicating if the connection is valid.
        """
        if self.url is None:
            log.error("URL is not properly set for REST API connection.")
            return False

        try:
            response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                log.info(f"REST connection is valid for URL: {self.url}")
                return True
            else:
                log.error(f"REST connection validation failed: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            log.error(f"An error occurred while validating REST connection: {e}")
            return False

    def post(self, payload):
        """
        Sends a POST request to the specified REST API endpoint with the provided payload.

        :param payload: The data to be sent in the POST request.
        :return: Response object from the POST request.
        :raises ConnectionError: If the request fails.
        """
        if not self.is_connected:
            log.error("No active connection. Please connect first before making a request.")
            raise ConnectionError("No active connection. Please connect first before making a request.")

        try:
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=self.timeout)
            log.info(f"POST to {self.url} with payload {payload} - Status Code: {response.status_code}")
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            log.error(f"Failed to POST to {self.url}: {e}")
            raise ConnectionError(f"Failed to POST to REST API at: {self.url}")

    def get_env_keys(self) -> list:
        """
        Provides the list of environment variable keys required for REST connection.
        Note: This connector may use environment variables for base URL or headers if applicable.

        :return: List of environment keys, such as ['REST_API_BASE_URL', 'REST_API_HEADERS']
        """
        return ['REST_API_BASE_URL', 'REST_API_HEADERS']

    def pre_connect_hook(self, **kwargs):
        """
        Hook method to add any REST-specific operations before connecting.
        Can be overridden by subclasses to perform additional actions.

        :param kwargs: Additional parameters for pre-connect setup.
        """
        log.info(f"Running pre-connect hook for REST Connector with name: {self.name}")
        # Add any pre-connect setup specific to REST here
        pass

    def post_connect_hook(self):
        """
        Hook method to add any REST-specific operations after connecting.
        Can be overridden by subclasses to perform additional actions.
        """
        log.info(f"Running post-connect hook for REST Connector with name: {self.name}")
        # Add any post-connect actions specific to REST here
        pass