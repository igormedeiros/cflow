# File: google_sheets.py
import os
from typing import Optional, List, Any
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class GoogleSheetsConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "GoogleSheetsConnector",
            description: Optional[str] = None,
            credentials_json: Optional[str] = None,
            spreadsheet_name: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the GoogleSheetsConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Google Sheets",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.credentials_json = credentials_json or os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
        self.spreadsheet_name = spreadsheet_name or os.getenv('GOOGLE_SHEET_NAME')
        self.client = None
        self.spreadsheet = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with Google Sheets."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_json, scope)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open(self.spreadsheet_name)

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to Google Sheets: {self.spreadsheet_name}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Google Sheets connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Google Sheets")
            raise

    def disconnect(self) -> None:
        """Disconnects from Google Sheets."""
        try:
            log.info(f"Disconnecting from Google Sheets: {self.spreadsheet_name}")
            self.client = None
            self.spreadsheet = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Google Sheets disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Google Sheets."""
        try:
            if not self.client or not self.spreadsheet:
                return False
            # Attempt to access a worksheet to validate the connection
            self.spreadsheet.worksheets()
            return True
        except Exception as e:
            self._handle_exception(e, "Google Sheets connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['GOOGLE_SHEETS_CREDENTIALS_JSON', 'GOOGLE_SHEET_NAME']

    def get_data(self, sheet_name: str) -> List[List[Any]]:
        """Retrieves data from a specified sheet in Google Sheets."""
        if not self.connected:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            data = sheet.get_all_values()
            log.info(f"Successfully retrieved data from sheet: {sheet_name}")
            return data
        except Exception as e:
            self._handle_exception(e, f"Failed to get data from sheet: {sheet_name}")
            raise

    def update_data(self, sheet_name: str, cell_range: str, values: List[List[Any]]) -> bool:
        """Updates a range of cells in a specified sheet in Google Sheets."""
        if not self.connected:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            cell_range_update = sheet.range(cell_range)
            for i, cell in enumerate(cell_range_update):
                cell.value = values[i // len(values[0])][i % len(values[0])]
            sheet.update_cells(cell_range_update)
            log.info(f"Successfully updated data in sheet: {sheet_name}, range: {cell_range}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to update data in sheet: {sheet_name}, range: {cell_range}")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False
