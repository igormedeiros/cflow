# File: ftp_connector.py
import os
from typing import Optional, List
from ftplib import FTP, error_perm
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class FTPConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "FTPConnector",
            description: Optional[str] = None,
            host: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            port: int = 21,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the FTPConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for FTP integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.host = host or os.getenv('FTP_HOST')
        self.username = username or os.getenv('FTP_USERNAME')
        self.password = password or os.getenv('FTP_PASSWORD')
        self.port = port
        self.ftp = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with the FTP server."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            self.ftp = FTP()
            self.ftp.connect(host=self.host, port=self.port, timeout=self.timeout)
            self.ftp.login(user=self.username, passwd=self.password)

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to FTP server: {self.host}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate FTP connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to FTP")
            raise

    def disconnect(self) -> None:
        """Disconnects from the FTP server."""
        try:
            log.info(f"Disconnecting from FTP server: {self.host}")
            if self.ftp:
                self.ftp.quit()
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during FTP disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to the FTP server."""
        try:
            if not self.ftp:
                return False
            # Attempt to list the root directory to validate the connection
            self.ftp.cwd('/')
            return True
        except error_perm as e:
            self._handle_exception(e, "FTP connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['FTP_HOST', 'FTP_USERNAME', 'FTP_PASSWORD']

    def upload_file(self, local_file_path: str, remote_file_path: str) -> bool:
        """Uploads a file to the FTP server."""
        if not self.connected:
            raise ConnectionError("Not connected to FTP server")

        try:
            with open(local_file_path, 'rb') as file:
                self.ftp.storbinary(f'STOR {remote_file_path}', file)
            log.info(f"Successfully uploaded file to FTP server: {remote_file_path}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to upload file: {local_file_path}")
            return False

    def download_file(self, remote_file_path: str, local_file_path: str) -> bool:
        """Downloads a file from the FTP server."""
        if not self.connected:
            raise ConnectionError("Not connected to FTP server")

        try:
            with open(local_file_path, 'wb') as file:
                self.ftp.retrbinary(f'RETR {remote_file_path}', file.write)
            log.info(f"Successfully downloaded file from FTP server: {remote_file_path}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to download file: {remote_file_path}")
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