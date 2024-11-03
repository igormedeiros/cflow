# File: csv_file_connector.py
import os
import csv
from typing import Optional, List, Any
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class CSVFileConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "CSVFileConnector",
            description: Optional[str] = None,
            file_path: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the CSVFileConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for reading and writing CSV files",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.file_path = file_path or os.getenv('CSV_FILE_PATH')
        self.data = None
        if not self.file_path:
            raise ValueError("CSV file path must be provided for CSVFileConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection by loading the CSV file specified."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self.load_csv_file()
            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to CSV file at: {self.file_path}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate CSV file connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to CSV file")
            raise

    def disconnect(self) -> None:
        """Disconnects from the CSV file."""
        try:
            log.info(f"Disconnecting from CSV file at: {self.file_path}")
            self.data = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during CSV file disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if the CSV file has been successfully loaded."""
        if self.data is not None:
            log.info(f"CSV file connection is valid for file at: {self.file_path}")
            return True
        else:
            log.error(f"CSV file connection is not valid for file at: {self.file_path}")
            return False

    def load_csv_file(self) -> None:
        """Loads data from the CSV file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                self.data = [row for row in reader]
                log.info(f"Successfully loaded CSV file at: {self.file_path}")
        except FileNotFoundError as e:
            log.error(f"Failed to connect to CSV file: {e}")
            raise FileNotFoundError(f"Unable to locate CSV file at: {self.file_path}")
        except Exception as e:
            log.error(f"An error occurred while loading CSV file: {e}")
            raise ConnectionError(f"Unable to load CSV file: {e}")

    def get_data(self) -> List[Dict[str, Any]]:
        """Retrieves the data from the loaded CSV file."""
        if self.data is None:
            log.error("No data loaded. Please connect to the CSV file first.")
            raise ConnectionError("No data loaded. Please connect to the CSV file first.")
        return self.data

    def write_data(self, data: List[Dict[str, Any]]) -> None:
        """Writes data to the CSV file."""
        if not self.connected:
            raise ConnectionError("Not connected to CSV file")

        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as csv_file:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                    log.info(f"Successfully wrote data to CSV file at: {self.file_path}")
                    self.data = data
        except Exception as e:
            self._handle_exception(e, "Failed to write data to CSV file")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for CSV connection."""
        return ['CSV_FILE_PATH']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False