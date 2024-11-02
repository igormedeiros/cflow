# Arquivo: src/connectors/telegram_connector/telegram_connector.py

from src.cflow.connector_base import ConnectorBase
import requests
from logger import log
import os


class TelegramConnector(ConnectorBase):
    def __init__(self, name="TelegramConnector", description=None, token=None, chat_id=None, retry_attempts=3,
                 timeout=30, enable_retry=True):
        """
        Initializes the TelegramConnector instance with specific parameters.

        :param name: Name of the connector.
        :param description: Optional description of the connector.
        :param token: Telegram Bot token for authentication.
        :param chat_id: The chat ID where messages will be sent.
        :param retry_attempts: Number of times to retry the connection in case of failure.
        :param timeout: Timeout value for the connection.
        :param enable_retry: Flag to enable or disable retry attempts.
        """
        super().__init__(name, description if description else "Sends notifications via Telegram", retry_attempts,
                         timeout, enable_retry)
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.setup_connector()

    def setup_connector(self):
        """
        Initial setup of the Telegram connector.
        Defines specific variables and additional settings required for the proper functioning of the connector.
        """
        log.info(f"Setting up Telegram Connector with name: {self.name}")
        if not self.token or not self.chat_id:
            log.error("Telegram token or chat ID is not provided.")
            raise ValueError("Telegram token and chat ID must be provided for TelegramConnector.")

    def connect(self, **kwargs) -> None:
        """
        Establishes a connection to prepare for sending messages via Telegram.

        :param kwargs: Additional parameters required for connection.
        """
        log.info(f"Ready to send Telegram notifications to chat ID: {self.chat_id}")
        # No actual connection to establish; setting internal state to connected
        self.is_connected = True

    def disconnect(self) -> None:
        """
        Disconnects from Telegram.
        Sets the internal state to disconnected.
        """
        log.info(f"Disconnecting from Telegram notifications for chat ID: {self.chat_id}")
        self.is_connected = False

    def validate_connection(self) -> bool:
        """
        Validates if the Telegram connection is still valid by sending a test message.

        :return: Boolean indicating if the connection is valid.
        """
        log.info(f"Validating Telegram connection for chat ID: {self.chat_id}")
        try:
            response = self.notify(message="Validation message from Telegram Connector.")
            if response.status_code == 200:
                log.info("Telegram connection is valid.")
                return True
            else:
                log.error(f"Telegram connection validation failed: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            log.error(f"An error occurred while validating Telegram connection: {e}")
            return False

    def notify(self, message="Workflow completed successfully."):
        """
        Sends a notification message to the specified Telegram chat.

        :param message: The text message to send.
        :return: Response object from the Telegram API.
        :raises ConnectionError: If the notification fails.
        """
        if not self.is_connected:
            log.error("No active connection. Please connect first before sending a notification.")
            raise ConnectionError("No active connection. Please connect first before sending a notification.")

        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        try:
            response = requests.post(self.base_url, json=payload, timeout=self.timeout)
            log.info(f"Notification sent to Telegram - Status Code: {response.status_code}")
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            log.error(f"Failed to send notification to Telegram: {e}")
            raise ConnectionError(f"Failed to send notification to Telegram for chat ID: {self.chat_id}")

    def get_env_keys(self) -> list:
        """
        Provides the list of environment variable keys required for Telegram connection.

        :return: List of keys, such as ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
        """
        return ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']

    def pre_connect_hook(self, **kwargs):
        """
        Hook method to add any Telegram-specific operations before connecting.
        Can be overridden by subclasses to perform additional actions.

        :param kwargs: Additional parameters for pre-connect setup.
        """
        log.info(f"Running pre-connect hook for Telegram Connector with name: {self.name}")
        # Add any pre-connect setup specific to Telegram here
        pass

    def post_connect_hook(self):
        """
        Hook method to add any Telegram-specific operations after connecting.
        Can be overridden by subclasses to perform additional actions.
        """
        log.info(f"Running post-connect hook for Telegram Connector with name: {self.name}")
        # Add any post-connect actions specific to Telegram here
        pass
