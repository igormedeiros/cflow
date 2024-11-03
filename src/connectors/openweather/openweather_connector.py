# File: openweather_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class OpenWeatherConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "OpenWeatherConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the OpenWeatherConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for OpenWeather integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5')
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.headers = {
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with OpenWeather API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to OpenWeather API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate OpenWeather connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to OpenWeather")
            raise

    def disconnect(self) -> None:
        """Disconnects from OpenWeather API."""
        try:
            log.info("Disconnecting from OpenWeather API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during OpenWeather disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to OpenWeather API."""
        try:
            if not self.base_url or not self.api_key:
                return False
            url = f"{self.base_url}/weather?q=London&appid={self.api_key}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "OpenWeather connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['OPENWEATHER_BASE_URL', 'OPENWEATHER_API_KEY']

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Gets current weather data for a specified city from OpenWeather."""
        if not self.connected:
            raise ConnectionError("Not connected to OpenWeather API")

        try:
            url = f"{self.base_url}/weather?q={city}&appid={self.api_key}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            weather_data = response.json()
            log.info(f"Successfully retrieved current weather for city: {city}")
            return weather_data
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve current weather for city: {city}")
            return {}

    def get_weather_forecast(self, city: str) -> Dict[str, Any]:
        """Gets 5-day weather forecast for a specified city from OpenWeather."""
        if not self.connected:
            raise ConnectionError("Not connected to OpenWeather API")

        try:
            url = f"{self.base_url}/forecast?q={city}&appid={self.api_key}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            forecast_data = response.json()
            log.info(f"Successfully retrieved weather forecast for city: {city}")
            return forecast_data
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve weather forecast for city: {city}")
            return {}

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False