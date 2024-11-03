# File: anthropic_connector.py
import os
import requests
from typing import Optional, List
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class AnthropicConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "AnthropicConnector",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            model: str = "claude-v1",
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the AnthropicConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Anthropic API integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/complete"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Anthropic API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Anthropic API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Anthropic connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Anthropic API")
            raise

    def disconnect(self) -> None:
        """Disconnects from Anthropic API."""
        try:
            log.info("Disconnecting from Anthropic API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Anthropic disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Anthropic API."""
        try:
            if not self.api_key:
                log.error("Anthropic API key is not provided.")
                return False
            # Perform a simple request to validate the connection
            payload = {
                "model": self.model,
                "prompt": "Hello, Anthropic!",
                "max_tokens_to_sample": 5
            }
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Anthropic connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['ANTHROPIC_API_KEY']

    def generate_text(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generates text using the Anthropic API."""
        if not self.connected:
            raise ConnectionError("Not connected to Anthropic API")

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens_to_sample": max_tokens,
                "temperature": temperature
            }
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            generated_text = response.json().get("completion", "").strip()
            log.info("Successfully generated text using Anthropic API")
            return generated_text
        except Exception as e:
            self._handle_exception(e, "Failed to generate text using Anthropic API")
            return ""

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False