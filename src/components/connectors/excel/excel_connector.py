# Arquivo: src/connectors/excel_connector/excel_connector.py

import pandas as pd

from core.connector.connector_base import ConnectorBase
from core.logger import log


class ExcelConnector(ConnectorBase):
    def __init__(self, name="ExcelConnector", description=None, file_path=None, retry_attempts=3, timeout=30,
                 enable_retry=True):
        """
        Initializes the ExcelConnector instance with specific parameters.

        :param name: Name of the connector.
        :param description: Optional description of the connector.
        :param file_path: Path to the Excel file to be read.
        :param retry_attempts: Number of times to retry the connection in case of failure.
        :param timeout: Timeout value for the connection.
        :param enable_retry: Flag to enable or disable retry attempts.
        """
        super().__init__(name, description if description else "Reads data from an Excel file", retry_attempts, timeout,
                         enable_retry)
        self.file_path = file_path
        self.data = None
        self.setup_connector()

    def setup_connector(self):
        """
        Initial setup of the Excel connector.
        Defines specific variables and additional settings required for the proper functioning of the connector.
        """
        log.info(f"Setting up Excel Connector with name: {self.name}")
        if not self.file_path:
            log.error("Excel file path is not provided.")
            raise ValueError("Excel file path must be provided for ExcelConnector.")

    def connect(self, **kwargs) -> None:
        """
        Establishes a connection by loading the Excel file specified.

        :param kwargs: Additional parameters required for connection.
        :raises FileNotFoundError: If the Excel file cannot be found.
        """
        log.info(f"Connecting to Excel file at: {self.file_path}")
        try:
            self.data = pd.read_excel(self.file_path)
            log.info(f"Successfully connected to Excel file at: {self.file_path}")
        except FileNotFoundError as e:
            log.error(f"Failed to connect to Excel file: {e}")
            raise FileNotFoundError(f"Unable to locate Excel file at: {self.file_path}")
        except Exception as e:
            log.error(f"An error occurred while connecting to Excel file: {e}")
            raise ConnectionError(f"Unable to connect to Excel file: {e}")

    def disconnect(self) -> None:
        """
        Disconnects from the Excel data.
        Sets the internal state to disconnected and clears the loaded data.
        """
        log.info(f"Disconnecting from Excel file at: {self.file_path}")
        self.data = None
        self.is_connected = False

    def validate_connection(self) -> bool:
        """
        Validates if the Excel file has been successfully loaded.

        :return: Boolean indicating if the connection is valid.
        """
        if self.data is not None:
            log.info(f"Excel connection is valid for file at: {self.file_path}")
            return True
        else:
            log.error(f"Excel connection is not valid for file at: {self.file_path}")
            return False

    def get_data(self):
        """
        Retrieves the data from the loaded Excel file.

        :return: Pandas DataFrame containing the data from the Excel file.
        :raises ConnectionError: If no data is loaded (i.e., not connected).
        """
        if self.data is None:
            log.error("No data loaded. Please connect to the Excel file first.")
            raise ConnectionError("No data loaded. Please connect to the Excel file first.")
        return self.data

    def get_env_keys(self) -> list:
        """
        Provides the list of environment variable keys required for Excel connection.
        Note: This connector does not require environment variables.

        :return: Empty list as no environment variables are required.
        """
        return []

    def pre_connect_hook(self, **kwargs):
        """
        Hook method to add any Excel-specific operations before connecting.
        Can be overridden by subclasses to perform additional actions.

        :param kwargs: Additional parameters for pre-connect setup.
        """
        log.info(f"Running pre-connect hook for Excel Connector with name: {self.name}")
        # Add any pre-connect setup specific to Excel here
        pass

    def post_connect_hook(self):
        """
        Hook method to add any Excel-specific operations after connecting.
        Can be overridden by subclasses to perform additional actions.
        """
        log.info(f"Running post-connect hook for Excel Connector with name: {self.name}")
        # Add any post-connect actions specific to Excel here
        pass
