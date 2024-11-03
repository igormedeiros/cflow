# File: google_drive_connector.py
import os
from typing import Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log
import io


class GoogleDriveConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "GoogleDriveConnector",
            description: Optional[str] = None,
            credentials_file: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the GoogleDriveConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Google Drive integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.credentials_file = credentials_file or os.getenv('GOOGLE_DRIVE_CREDENTIALS_FILE')
        self.service = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with Google Drive API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            credentials = service_account.Credentials.from_service_account_file(self.credentials_file, scopes=[
                'https://www.googleapis.com/auth/drive'])
            self.service = build('drive', 'v3', credentials=credentials)

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Google Drive API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Google Drive connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Google Drive")
            raise

    def disconnect(self) -> None:
        """Disconnects from Google Drive API."""
        try:
            log.info("Disconnecting from Google Drive API")
            self.service = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Google Drive disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Google Drive API."""
        try:
            if not self.service:
                return False
            # Attempt to list files to validate the connection
            results = self.service.files().list(pageSize=1).execute()
            return 'files' in results
        except Exception as e:
            self._handle_exception(e, "Google Drive connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['GOOGLE_DRIVE_CREDENTIALS_FILE']

    def upload_file(self, local_file_path: str, remote_file_name: str) -> bool:
        """Uploads a file to Google Drive."""
        if not self.connected:
            raise ConnectionError("Not connected to Google Drive API")

        try:
            file_metadata = {'name': remote_file_name}
            media = MediaFileUpload(local_file_path, resumable=True)
            self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            log.info(f"Successfully uploaded file to Google Drive: {remote_file_name}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to upload file: {local_file_path}")
            return False

    def download_file(self, file_id: str, local_file_path: str) -> bool:
        """Downloads a file from Google Drive."""
        if not self.connected:
            raise ConnectionError("Not connected to Google Drive API")

        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(local_file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                log.info(f"Download progress: {int(status.progress() * 100)}%%")
            log.info(f"Successfully downloaded file from Google Drive: {file_id}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to download file: {file_id}")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False