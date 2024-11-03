# File: json_file_connector.py
import os
import json
from typing import Optional, List, Dict, Any
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class JSONFileConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "JSONFileConnector",
            description: Optional[str] = None,
            file_path: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the JSONFileConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for reading and writing JSON files",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.file_path = file_path or os.getenv('JSON_FILE_PATH')
        self.data = None
        if not self.file_path:
            raise ValueError("JSON file path must be provided for JSONFileConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection by loading the JSON file specified."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self.load_json_file()
            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to JSON file at: {self.file_path}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate JSON file connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to JSON file")
            raise

    def disconnect(self) -> None:
        """Disconnects from the JSON file."""
        try:
            log.info(f"Disconnecting from JSON file at: {self.file_path}")
            self.data = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during JSON file disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if the JSON file has been successfully loaded."""
        if self.data is not None:
            log.info(f"JSON file connection is valid for file at: {self.file_path}")
            return True
        else:
            log.error(f"JSON file connection is not valid for file at: {self.file_path}")
            return False

    def load_json_file(self) -> None:
        """Loads data from the JSON file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as json_file:
                self.data = json.load(json_file)
                log.info(f"Successfully loaded JSON file at: {self.file_path}")
        except FileNotFoundError as e:
            log.error(f"Failed to connect to JSON file: {e}")
            raise FileNotFoundError(f"Unable to locate JSON file at: {self.file_path}")
        except json.JSONDecodeError as e:
            log.error(f"Error decoding JSON file: {e}")
            raise ValueError(f"Error decoding JSON file at: {self.file_path}")
        except Exception as e:
            log.error(f"An error occurred while loading JSON file: {e}")
            raise ConnectionError(f"Unable to load JSON file: {e}")

    def get_data(self) -> Dict[str, Any]:
        """Retrieves the data from the loaded JSON file."""
        if self.data is None:
            log.error("No data loaded. Please connect to the JSON file first.")
            raise ConnectionError("No data loaded. Please connect to the JSON file first.")
        return self.data

    def write_data(self, data: Dict[str, Any]) -> None:
        """Writes data to the JSON file."""
        if not self.connected:
            raise ConnectionError("Not connected to JSON file")

        try:
            with open(self.file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
                log.info(f"Successfully wrote data to JSON file at: {self.file_path}")
                self.data = data
        except Exception as e:
            self._handle_exception(e, "Failed to write data to JSON file")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for JSON connection."""
        return ['JSON_FILE_PATH']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False
