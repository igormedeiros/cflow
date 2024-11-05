# File: sftp_connector.py
import os
from typing import Optional, List
import paramiko
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SFTPConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SFTPConnector",
            description: Optional[str] = None,
            host: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            port: int = 22,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SFTPConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for SFTP integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.host = host or os.getenv('SFTP_HOST')
        self.username = username or os.getenv('SFTP_USERNAME')
        self.password = password or os.getenv('SFTP_PASSWORD')
        self.port = port
        self.sftp = None
        self.transport = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with the SFTP server."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to SFTP server: {self.host}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate SFTP connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to SFTP")
            raise

    def disconnect(self) -> None:
        """Disconnects from the SFTP server."""
        try:
            log.info(f"Disconnecting from SFTP server: {self.host}")
            if self.sftp:
                self.sftp.close()
            if self.transport:
                self.transport.close()
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during SFTP disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to the SFTP server."""
        try:
            if not self.sftp:
                return False
            # Attempt to list the root directory to validate the connection
            self.sftp.listdir()
            return True
        except Exception as e:
            self._handle_exception(e, "SFTP connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SFTP_HOST', 'SFTP_USERNAME', 'SFTP_PASSWORD']

    def upload_file(self, local_file_path: str, remote_file_path: str) -> bool:
        """Uploads a file to the SFTP server."""
        if not self.connected:
            raise ConnectionError("Not connected to SFTP server")

        try:
            self.sftp.put(local_file_path, remote_file_path)
            log.info(f"Successfully uploaded file to SFTP server: {remote_file_path}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to upload file: {local_file_path}")
            return False

    def download_file(self, remote_file_path: str, local_file_path: str) -> bool:
        """Downloads a file from the SFTP server."""
        if not self.connected:
            raise ConnectionError("Not connected to SFTP server")

        try:
            self.sftp.get(remote_file_path, local_file_path)
            log.info(f"Successfully downloaded file from SFTP server: {remote_file_path}")
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