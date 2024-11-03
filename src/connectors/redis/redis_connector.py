# File: redis_connector.py
import os
from typing import Optional, List, Any
import redis
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class RedisConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "RedisConnector",
            description: Optional[str] = None,
            host: Optional[str] = None,
            port: int = 6379,
            db: int = 0,
            password: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the RedisConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Redis integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.db = db or int(os.getenv('REDIS_DB', 0))
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.client = None

    def connect(self, **kwargs) -> None:
        """Establishes connection to the Redis server."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)

            # Initialize Redis client
            self.client = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to Redis at: {self.host}:{self.port}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Redis connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Redis")
            raise

    def disconnect(self) -> None:
        """Disconnects from Redis."""
        try:
            log.info("Disconnecting from Redis")
            self.client = None
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Redis disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates if Redis connection is successful."""
        try:
            if self.client.ping():
                log.info("Redis connection validated successfully")
                return True
            else:
                return False
        except Exception as e:
            self._handle_exception(e, "Redis connection validation failed")
            return False

    def set_value(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """Sets a value in Redis with an optional expiration time."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to Redis")

        try:
            self.client.set(name=key, value=value, ex=expire)
            log.info(f"Successfully set key '{key}' in Redis")
        except Exception as e:
            self._handle_exception(e, f"Failed to set key '{key}' in Redis")
            raise

    def get_value(self, key: str) -> Any:
        """Gets a value from Redis."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to Redis")

        try:
            value = self.client.get(key)
            log.info(f"Successfully retrieved key '{key}' from Redis")
            return value
        except Exception as e:
            self._handle_exception(e, f"Failed to get key '{key}' from Redis")
            return None

    def delete_key(self, key: str) -> None:
        """Deletes a key from Redis."""
        if not self.connected or not self.client:
            raise ConnectionError("Not connected to Redis")

        try:
            self.client.delete(key)
            log.info(f"Successfully deleted key '{key}' from Redis")
        except Exception as e:
            self._handle_exception(e, f"Failed to delete key '{key}' from Redis")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Redis connection."""
        return ['REDIS_HOST', 'REDIS_PORT', 'REDIS_DB', 'REDIS_PASSWORD']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False