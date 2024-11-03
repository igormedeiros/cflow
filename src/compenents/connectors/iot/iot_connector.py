# File: iot_connector.py
import os
from typing import Optional, List
import paho.mqtt.client as mqtt
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class IoTConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "IoTConnector",
            description: Optional[str] = None,
            broker_url: Optional[str] = None,
            broker_port: int = 1883,
            client_id: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the IoTConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for IoT MQTT integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.broker_url = broker_url or os.getenv('IOT_BROKER_URL')
        self.broker_port = broker_port
        self.client_id = client_id or os.getenv('IOT_CLIENT_ID', "IoT_Client")
        self.username = username or os.getenv('IOT_USERNAME')
        self.password = password or os.getenv('IOT_PASSWORD')
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.connected = False

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

    def connect(self, **kwargs) -> None:
        """Establishes connection with the MQTT broker."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self.client.connect(self.broker_url, self.broker_port, keepalive=self.timeout)
            self.client.loop_start()
            log.info(f"Successfully connected to MQTT broker at {self.broker_url}:{self.broker_port}")
            self.post_connect_hook()
        except Exception as e:
            self._handle_exception(e, "Failed to connect to MQTT broker")
            raise

    def disconnect(self) -> None:
        """Disconnects from the MQTT broker."""
        try:
            log.info("Disconnecting from MQTT broker")
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during MQTT disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to the MQTT broker."""
        return self.connected

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            log.info(f"Connected to MQTT Broker: {self.broker_url}")
            self.connected = True
        else:
            log.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        log.info("Disconnected from MQTT Broker")
        self.connected = False

    def on_message(self, client, userdata, message):
        log.info(f"Received message: {str(message.payload.decode())} on topic {message.topic}")

    def publish(self, topic: str, payload: str, qos: int = 1) -> bool:
        """Publishes a message to a specified topic."""
        if not self.connected:
            raise ConnectionError("Not connected to MQTT Broker")

        try:
            result = self.client.publish(topic, payload, qos)
            status = result[0]
            if status == 0:
                log.info(f"Successfully sent message to topic {topic}")
                return True
            else:
                log.error(f"Failed to send message to topic {topic}")
                return False
        except Exception as e:
            self._handle_exception(e, f"Failed to publish message to topic {topic}")
            return False

    def subscribe(self, topic: str, qos: int = 1) -> None:
        """Subscribes to a specified topic."""
        if not self.connected:
            raise ConnectionError("Not connected to MQTT Broker")

        try:
            self.client.subscribe(topic, qos)
            log.info(f"Subscribed to topic {topic}")
        except Exception as e:
            self._handle_exception(e, f"Failed to subscribe to topic {topic}")
            raise

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['IOT_BROKER_URL', 'IOT_CLIENT_ID', 'IOT_USERNAME', 'IOT_PASSWORD']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            self.publish("notifications", message or default_message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False