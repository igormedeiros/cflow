# File: mysql_connector.py
import os
from typing import Optional, List, Any, Dict
import mysql.connector
from mysql.connector import Error
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class MySQLConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "MySQLConnector",
            description: Optional[str] = None,
            host: Optional[str] = None,
            database: Optional[str] = None,
            user: Optional[str] = None,
            password: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the MySQLConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for MySQL integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.host = host or os.getenv('MYSQL_HOST')
        self.database = database or os.getenv('MYSQL_DATABASE')
        self.user = user or os.getenv('MYSQL_USER')
        self.password = password or os.getenv('MYSQL_PASSWORD')
        self.connection = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with MySQL database."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=self.timeout
            )

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to MySQL database: {self.database}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate MySQL connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to MySQL")
            raise

    def disconnect(self) -> None:
        """Disconnects from MySQL database."""
        try:
            log.info(f"Disconnecting from MySQL database: {self.database}")
            if self.connection:
                self.connection.close()
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during MySQL disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to MySQL database."""
        try:
            if not self.connection:
                return False
            if self.connection.is_connected():
                return True
            else:
                return False
        except Error as e:
            self._handle_exception(e, "MySQL connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['MYSQL_HOST', 'MYSQL_DATABASE', 'MYSQL_USER', 'MYSQL_PASSWORD']

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """Executes a query in the MySQL database."""
        if not self.connected:
            raise ConnectionError("Not connected to MySQL")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            self.connection.commit()
            log.info(f"Successfully executed query: {query}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to execute query: {query}")
            return False
        finally:
            cursor.close()

    def fetch_results(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetches results from a query in the MySQL database."""
        if not self.connected:
            raise ConnectionError("Not connected to MySQL")

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or {})
            results = cursor.fetchall()
            log.info(f"Successfully fetched results for query: {query}")
            return results
        except Exception as e:
            self._handle_exception(e, f"Failed to fetch results for query: {query}")
            return []
        finally:
            cursor.close()

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False
