# File: trello_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class TrelloConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "TrelloConnector",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            api_token: Optional[str] = None,
            board_id: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the TrelloConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Trello integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('TRELLO_API_KEY')
        self.api_token = api_token or os.getenv('TRELLO_API_TOKEN')
        self.board_id = board_id or os.getenv('TRELLO_BOARD_ID')
        self.base_url = "https://api.trello.com/1"
        self.headers = {
            "Accept": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Trello API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Trello API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Trello connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Trello")
            raise

    def disconnect(self) -> None:
        """Disconnects from Trello API."""
        try:
            log.info("Disconnecting from Trello API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Trello disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Trello API."""
        try:
            if not self.api_key or not self.api_token or not self.board_id:
                return False
            url = f"{self.base_url}/boards/{self.board_id}"
            response = requests.get(url, params=self._auth_params(), headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Trello connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['TRELLO_API_KEY', 'TRELLO_API_TOKEN', 'TRELLO_BOARD_ID']

    def create_card(self, list_id: str, card_name: str, card_desc: Optional[str] = None) -> bool:
        """Creates a new card in the specified Trello list."""
        if not self.connected:
            raise ConnectionError("Not connected to Trello API")

        try:
            url = f"{self.base_url}/cards"
            payload = {
                "idList": list_id,
                "name": card_name,
                "desc": card_desc or "",
                "key": self.api_key,
                "token": self.api_token
            }
            response = requests.post(url, params=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created card in Trello list: {list_id}")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create card in Trello")
            return False

    def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """Gets all cards from a specified Trello list."""
        if not self.connected:
            raise ConnectionError("Not connected to Trello API")

        try:
            url = f"{self.base_url}/lists/{list_id}/cards"
            response = requests.get(url, params=self._auth_params(), headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            cards = response.json()
            log.info(f"Successfully retrieved cards from Trello list: {list_id}")
            return cards
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve cards from Trello")
            return []

    def _auth_params(self) -> Dict[str, str]:
        """Returns authentication parameters for Trello API requests."""
        return {
            "key": self.api_key,
            "token": self.api_token
        }

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False