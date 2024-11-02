# Arquivo: src/connectors/trello_connector/trello_connector.py

from src.cflow.connector_base import ConnectorBase
import requests
from logger import log
import os


class TrelloConnector(ConnectorBase):
    def __init__(self, name="TrelloConnector", description=None, retry_attempts=3, timeout=30, enable_retry=True):
        """
        Initializes the TrelloConnector instance with specific parameters.

        :param name: Name of the connector.
        :param description: Optional description of the connector.
        :param retry_attempts: Number of times to retry the connection in case of failure.
        :param timeout: Timeout value for the connection.
        :param enable_retry: Flag to enable or disable retry attempts.
        """
        super().__init__(name, description if description else "Connects to Trello API", retry_attempts, timeout,
                         enable_retry)
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.base_url = "https://api.trello.com/1/"
        self.setup_connector()

    def setup_connector(self):
        """
        Initial setup of the Trello connector.
        Defines specific variables and additional settings required for the proper functioning of the connector.
        """
        log.info(f"Setting up Trello Connector with name: {self.name}")
        if not self.api_key or not self.token:
            log.error("Trello API key or token is not provided.")
            raise ValueError("Trello API key and token must be provided for TrelloConnector.")
        self.pre_connect_hook()

    def connect(self, **kwargs) -> None:
        """
        Establishes a connection to the Trello API using provided credentials.

        :param kwargs: Additional parameters required for connection.
        :raises ConnectionError: If unable to connect to Trello API.
        """
        log.info(f"Connecting to Trello API with name: {self.name}")
        # Attempt to connect by hitting a basic Trello API endpoint to verify credentials
        response = requests.get(f"{self.base_url}members/me", params={"key": self.api_key, "token": self.token},
                                timeout=self.timeout)
        if response.status_code == 200:
            log.info("Successfully connected to Trello API.")
            self.is_connected = True
            self.post_connect_hook()
        else:
            log.error(f"Failed to connect to Trello API: {response.status_code} - {response.text}")
            raise ConnectionError("Unable to connect to Trello API.")

    def disconnect(self) -> None:
        """
        Disconnects from the Trello API.
        Sets the internal state to disconnected.
        """
        log.info(f"Disconnecting from Trello API with name: {self.name}")
        self.is_connected = False

    def validate_connection(self) -> bool:
        """
        Validates if the Trello connection is still active by checking the API credentials.

        :return: Boolean indicating if the connection is valid.
        """
        log.info(f"Validating Trello connection with name: {self.name}")
        try:
            response = requests.get(f"{self.base_url}members/me", params={"key": self.api_key, "token": self.token},
                                    timeout=self.timeout)
            if response.status_code == 200:
                log.info("Trello connection is valid.")
                return True
            else:
                log.error(f"Trello connection validation failed: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            log.error(f"An error occurred while validating Trello connection: {e}")
            return False

    def get_boards(self):
        """
        Retrieves the list of boards accessible by the authenticated user.

        :return: JSON response containing the list of boards.
        :raises ConnectionError: If unable to retrieve boards from Trello API.
        """
        log.info(f"Retrieving boards for Trello Connector with name: {self.name}")
        response = requests.get(f"{self.base_url}members/me/boards", params={"key": self.api_key, "token": self.token},
                                timeout=self.timeout)
        if response.status_code == 200:
            return response.json()
        else:
            log.error(f"Failed to get boards: {response.status_code} - {response.text}")
            raise ConnectionError("Unable to retrieve boards.")

    def create_card(self, list_id, card_name, card_desc=""):
        """
        Creates a new card in the specified Trello list.

        :param list_id: The ID of the Trello list where the card will be created.
        :param card_name: The name of the card to be created.
        :param card_desc: The description of the card to be created (optional).
        :return: JSON response containing the details of the created card.
        :raises ConnectionError: If unable to create card in Trello.
        """
        log.info(f"Creating card in list {list_id} for Trello Connector with name: {self.name}")
        data = {
            "name": card_name,
            "desc": card_desc,
            "idList": list_id,
            "key": self.api_key,
            "token": self.token
        }
        response = requests.post(f"{self.base_url}cards", json=data, timeout=self.timeout)
        if response.status_code == 200:
            return response.json()
        else:
            log.error(f"Failed to create card: {response.status_code} - {response.text}")
            raise ConnectionError("Unable to create card.")

    def get_env_keys(self) -> list:
        """
        Provides the list of environment variable keys required for Trello connection.

        :return: List of keys, such as ['TRELLO_API_KEY', 'TRELLO_TOKEN']
        """
        return ['TRELLO_API_KEY', 'TRELLO_TOKEN']

    def pre_connect_hook(self, **kwargs):
        """
        Hook method to add any Trello-specific operations before connecting.
        Can be overridden by subclasses to perform additional actions.

        :param kwargs: Additional parameters for pre-connect setup.
        """
        log.info(f"Running pre-connect hook for Trello Connector with name: {self.name}")
        # Add any pre-connect setup specific to Trello here
        pass

    def post_connect_hook(self):
        """
        Hook method to add any Trello-specific operations after connecting.
        Can be overridden by subclasses to perform additional actions.
        """
        log.info(f"Running post-connect hook for Trello Connector with name: {self.name}")
        # Add any post-connect actions specific to Trello here
        pass
