# File: smtp_connector.py
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, List

from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class SMTPConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "SMTPConnector",
            description: Optional[str] = None,
            smtp_server: Optional[str] = None,
            smtp_port: int = 587,
            username: Optional[str] = None,
            password: Optional[str] = None,
            use_tls: bool = True,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the SMTPConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for SMTP email sending",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER')
        self.smtp_port = smtp_port
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.use_tls = use_tls
        self.server = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with SMTP server."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()

            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
            if self.use_tls:
                self.server.starttls()
            self.server.login(self.username, self.password)

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to SMTP server")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate SMTP connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to SMTP server")
            raise

    def disconnect(self) -> None:
        """Disconnects from SMTP server."""
        try:
            log.info("Disconnecting from SMTP server")
            if self.server:
                self.server.quit()
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during SMTP disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to SMTP server."""
        try:
            if not self.server:
                return False
            status = self.server.noop()[0]
            return status == 250
        except Exception as e:
            self._handle_exception(e, "SMTP connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD']

    def send_email(self, to: str, subject: str, body: str, cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None) -> bool:
        """Sends an email through SMTP server."""
        if not self.connected:
            raise ConnectionError("Not connected to SMTP server")

        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject
            if cc:
                msg['Cc'] = ", ".join(cc)
            msg.attach(MIMEText(body, 'plain'))

            recipients = [to] + (cc if cc else []) + (bcc if bcc else [])
            self.server.sendmail(self.username, recipients, msg.as_string())
            log.info(f"Successfully sent email to {to}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to send email to {to}")
            return False

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            self.send_email(to=self.username, subject="Notification", body=message or default_message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False