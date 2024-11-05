# File: ssh_connector.py
import paramiko
import os
from typing import Optional, List
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SSHConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SSHConnector",
            description: Optional[str] = None,
            hostname: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            key_file: Optional[str] = None,
            port: int = 22,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SSHConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for SSH integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.hostname = hostname or os.getenv('SSH_HOSTNAME')
        self.username = username or os.getenv('SSH_USERNAME')
        self.password = password or os.getenv('SSH_PASSWORD')
        self.key_file = key_file or os.getenv('SSH_KEY_FILE')
        self.port = port
        self.client = None

    def connect(self, **kwargs) -> None:
        """Establishes SSH connection."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.key_file:
                self.client.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_file,
                    timeout=self.timeout
                )
            else:
                self.client.connect(
                    hostname=self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=self.timeout
                )

            self.connected = True
            log.info(f"Successfully connected to SSH server: {self.hostname}")
            self.post_connect_hook()
        except Exception as e:
            self._handle_exception(e, "Failed to connect to SSH server")
            raise

    def disconnect(self) -> None:
        """Disconnects from SSH server."""
        try:
            if self.client:
                self.client.close()
            self.connected = False
            log.info(f"Disconnected from SSH server: {self.hostname}")
        except Exception as e:
            self._handle_exception(e, "Error during SSH disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the SSH connection."""
        try:
            if not self.hostname or not self.username:
                return False
            # Simple validation by running a basic command
            stdin, stdout, stderr = self.client.exec_command('echo Connection Successful')
            return stdout.read().decode().strip() == "Connection Successful"
        except Exception as e:
            self._handle_exception(e, "SSH connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SSH_HOSTNAME', 'SSH_USERNAME', 'SSH_PASSWORD', 'SSH_KEY_FILE']

    def execute_command(self, command: str) -> str:
        """Executes a command on the SSH server and returns the output."""
        if not self.connected:
            raise ConnectionError("Not connected to SSH server")

        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode().strip()
            log.info(f"Command executed successfully on SSH server: {command}")
            return output
        except Exception as e:
            self._handle_exception(e, f"Failed to execute command on SSH server: {command}")
            return ""

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False