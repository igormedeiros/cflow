# File: notion_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class NotionConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "NotionConnector",
            description: Optional[str] = None,
            token: Optional[str] = None,
            database_id: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the NotionConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Notion integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.token = token or os.getenv('NOTION_TOKEN')
        self.database_id = database_id or os.getenv('NOTION_DATABASE_ID')
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Notion API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Notion API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Notion connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Notion")
            raise

    def disconnect(self) -> None:
        """Disconnects from Notion API."""
        try:
            log.info("Disconnecting from Notion API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Notion disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Notion API."""
        try:
            if not self.token or not self.database_id:
                return False
            response = requests.post(
                f"{self.base_url}/databases/{self.database_id}/query",
                headers=self.headers,
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Notion connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['NOTION_TOKEN', 'NOTION_DATABASE_ID']

    def create_page(self, page_properties: Dict[str, Any]) -> bool:
        """Creates a new page in the specified Notion database."""
        if not self.connected:
            raise ConnectionError("Not connected to Notion API")

        try:
            url = f"{self.base_url}/pages"
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": page_properties
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created page in Notion database: {self.database_id}")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create page in Notion")
            return False

    def query_database(self, query_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Queries the Notion database based on the provided filter."""
        if not self.connected:
            raise ConnectionError("Not connected to Notion API")

        try:
            url = f"{self.base_url}/databases/{self.database_id}/query"
            response = requests.post(url, json=query_filter or {}, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            results = response.json().get('results', [])
            log.info(f"Successfully queried Notion database: {self.database_id}")
            return results
        except Exception as e:
            self._handle_exception(e, "Failed to query Notion database")
            return []

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False