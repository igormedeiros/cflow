# File: openai_llm_connector.py
import os
import openai
from typing import Optional, List
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class OpenAILLMConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "OpenAILLMConnector",
            description: Optional[str] = None,
            api_key: Optional[str] = None,
            model: str = "text-davinci-003",
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the OpenAILLMConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for OpenAI Large Language Model (LLM) integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        openai.api_key = self.api_key

    def connect(self, **kwargs) -> None:
        """Establishes connection with OpenAI API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to OpenAI API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate OpenAI connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to OpenAI API")
            raise

    def disconnect(self) -> None:
        """Disconnects from OpenAI API."""
        try:
            log.info("Disconnecting from OpenAI API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during OpenAI disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to OpenAI API."""
        try:
            if not self.api_key:
                log.error("OpenAI API key is not provided.")
                return False
            # Perform a test completion request to validate the connection
            response = openai.Completion.create(
                model=self.model,
                prompt="Hello, OpenAI!",
                max_tokens=5
            )
            return response is not None
        except Exception as e:
            self._handle_exception(e, "OpenAI connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['OPENAI_API_KEY']

    def generate_text(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generates text using the OpenAI model."""
        if not self.connected:
            raise ConnectionError("Not connected to OpenAI API")

        try:
            response = openai.Completion.create(
                model=self.model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            generated_text = response.choices[0].text.strip()
            log.info("Successfully generated text using OpenAI API")
            return generated_text
        except Exception as e:
            self._handle_exception(e, "Failed to generate text using OpenAI API")
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