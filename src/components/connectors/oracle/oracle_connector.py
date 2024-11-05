# File: oracle_connector.py
import os
from typing import Optional, List, Dict, Any
import cx_Oracle
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class OracleConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "OracleConnector",
            description: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            dsn: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the Oracle Connector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Oracle Database integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.username = username or os.getenv('ORACLE_USERNAME')
        self.password = password or os.getenv('ORACLE_PASSWORD')
        self.dsn = dsn or os.getenv('ORACLE_DSN')
        self.connection = None

        if not self.username or not self.password or not self.dsn:
            raise ValueError("Username, Password, and DSN must be provided for OracleConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Oracle Database."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self.connection = cx_Oracle.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn
            )
            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Oracle Database")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Oracle Database connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Oracle Database")
            raise

    def validate_connection(self) -> bool:
        """Validates if Oracle Database connection is successful by executing a simple query."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.close()
            log.info("Oracle Database connection validated successfully")
            return True
        except Exception as e:
            self._handle_exception(e, "Oracle Database connection validation failed")
            return False

    def disconnect(self) -> None:
        """Disconnects from Oracle Database by closing the connection."""
        try:
            if self.connection:
                log.info("Disconnecting from Oracle Database")
                self.connection.close()
                self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Oracle Database disconnection")
            raise

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executes a query in Oracle Database and returns the result."""
        if not self.connected:
            raise ConnectionError("Not connected to Oracle Database")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            log.info(f"Successfully executed query: {query}")
            return result
        except Exception as e:
            self._handle_exception(e, f"Failed to execute query: {query}")
            raise

    def execute_non_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Executes a non-query statement (INSERT, UPDATE, DELETE) in Oracle Database."""
        if not self.connected:
            raise ConnectionError("Not connected to Oracle Database")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            self.connection.commit()
            cursor.close()
            log.info(f"Successfully executed non-query: {query}")
        except Exception as e:
            self._handle_exception(e, f"Failed to execute non-query: {query}")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Oracle Database connection."""
        return ['ORACLE_USERNAME', 'ORACLE_PASSWORD', 'ORACLE_DSN']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False