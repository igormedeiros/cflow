# File: txt_file_connector.py
import os
from typing import Optional, List, Any
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class TXTFileConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "TXTFileConnector",
            description: Optional[str] = None,
            file_path: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the TXTFileConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for reading and writing TXT files",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.file_path = file_path or os.getenv('TXT_FILE_PATH')
        self.data = None
        if not self.file_path:
            raise ValueError("TXT file path must be provided for TXTFileConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection by loading the TXT file specified."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self.load_txt_file()
            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to TXT file at: {self.file_path}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate TXT file connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to TXT file")
            raise

    def disconnect(self) -> None:
        """Disconnects from the TXT file."""
        try:
            log.info(f"Disconnecting from TXT file at: {self.file_path}")
            self.data = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during TXT file disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if the TXT file has been successfully loaded."""
        if self.data is not None:
            log.info(f"TXT file connection is valid for file at: {self.file_path}")
            return True
        else:
            log.error(f"TXT file connection is not valid for file at: {self.file_path}")
            return False

    def load_txt_file(self) -> None:
        """Loads data from the TXT file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as txt_file:
                self.data = txt_file.read()
                log.info(f"Successfully loaded TXT file at: {self.file_path}")
        except FileNotFoundError as e:
            log.error(f"Failed to connect to TXT file: {e}")
            raise FileNotFoundError(f"Unable to locate TXT file at: {self.file_path}")
        except Exception as e:
            log.error(f"An error occurred while loading TXT file: {e}")
            raise ConnectionError(f"Unable to load TXT file: {e}")

    def get_data(self) -> str:
        """Retrieves the data from the loaded TXT file."""
        if self.data is None:
            log.error("No data loaded. Please connect to the TXT file first.")
            raise ConnectionError("No data loaded. Please connect to the TXT file first.")
        return self.data

    def write_data(self, data: str) -> None:
        """Writes data to the TXT file."""
        if not self.connected:
            raise ConnectionError("Not connected to TXT file")

        try:
            with open(self.file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(data)
                log.info(f"Successfully wrote data to TXT file at: {self.file_path}")
                self.data = data
        except Exception as e:
            self._handle_exception(e, "Failed to write data to TXT file")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for TXT connection."""
        return ['TXT_FILE_PATH']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False