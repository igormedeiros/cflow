# File: kafka_connector.py
import os
from typing import Optional, List
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class KafkaConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "KafkaConnector",
            description: Optional[str] = None,
            bootstrap_servers: Optional[str] = None,
            topic: Optional[str] = None,
            group_id: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the KafkaConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Apache Kafka integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.bootstrap_servers = bootstrap_servers or os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        self.topic = topic or os.getenv('KAFKA_TOPIC')
        self.group_id = group_id or os.getenv('KAFKA_GROUP_ID')
        self.producer = None
        self.consumer = None
        if not self.bootstrap_servers or not self.topic:
            raise ValueError("Kafka bootstrap servers and topic must be provided for KafkaConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Kafka brokers."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)

            # Initialize Kafka Producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers.split(","),
                retries=self.retry_attempts
            )
            # Initialize Kafka Consumer if group_id is provided
            if self.group_id:
                self.consumer = KafkaConsumer(
                    self.topic,
                    group_id=self.group_id,
                    bootstrap_servers=self.bootstrap_servers.split(","),
                    auto_offset_reset='earliest',
                    enable_auto_commit=True
                )

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to Kafka at: {self.bootstrap_servers}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Kafka connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Kafka")
            raise

    def disconnect(self) -> None:
        """Disconnects from Kafka."""
        try:
            log.info("Disconnecting from Kafka")
            if self.producer:
                self.producer.close()
            if self.consumer:
                self.consumer.close()
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Kafka disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if Kafka connection is successful."""
        try:
            # Check producer initialization
            if self.producer:
                log.info("Kafka connection validated successfully")
                return True
            else:
                return False
        except Exception as e:
            self._handle_exception(e, "Kafka connection validation failed")
            return False

    def send_message(self, message: str) -> None:
        """Sends a message to the specified Kafka topic."""
        if not self.connected or not self.producer:
            raise ConnectionError("Not connected to Kafka")

        try:
            future = self.producer.send(self.topic, value=message.encode('utf-8'))
            future.add_callback(self.on_send_success).add_errback(self.on_send_error)
            log.info(f"Message sent to Kafka topic '{self.topic}'")
        except KafkaError as e:
            self._handle_exception(e, "Failed to send message to Kafka")
            raise

    def on_send_success(self, record_metadata) -> None:
        """Callback for successful message sending."""
        log.info(f"Message sent successfully to topic {record_metadata.topic} at partition {record_metadata.partition}")

    def on_send_error(self, excp) -> None:
        """Callback for message sending failure."""
        log.error(f"Failed to send message: {str(excp)}")

    def consume_messages(self) -> List[str]:
        """Consumes messages from the Kafka topic."""
        if not self.connected or not self.consumer:
            raise ConnectionError("Not connected to Kafka")

        try:
            messages = []
            for message in self.consumer:
                decoded_message = message.value.decode('utf-8')
                log.info(f"Consumed message: {decoded_message}")
                messages.append(decoded_message)
            return messages
        except KafkaError as e:
            self._handle_exception(e, "Failed to consume messages from Kafka")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Kafka connection."""
        return ['KAFKA_BOOTSTRAP_SERVERS', 'KAFKA_TOPIC', 'KAFKA_GROUP_ID']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False