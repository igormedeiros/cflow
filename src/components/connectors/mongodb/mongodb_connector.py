# File: mongodb_connector.py
import os
from typing import Optional, List, Any, Dict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class MongoDBConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "MongoDBConnector",
            description: Optional[str] = None,
            uri: Optional[str] = None,
            database_name: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the MongoDBConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for MongoDB integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.uri = uri or os.getenv('MONGODB_URI')
        self.database_name = database_name or os.getenv('MONGODB_DATABASE')
        self.client = None
        self.database = None

    def connect(self, **kwargs) -> None:
        """Establishes connection with MongoDB."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=self.timeout * 1000)
            self.database = self.client[self.database_name]

            if self.validate_connection():
                self.connected = True
                log.info(f"Successfully connected to MongoDB database: {self.database_name}")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate MongoDB connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to MongoDB")
            raise

    def disconnect(self) -> None:
        """Disconnects from MongoDB."""
        try:
            log.info(f"Disconnecting from MongoDB database: {self.database_name}")
            if self.client:
                self.client.close()
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during MongoDB disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to MongoDB."""
        try:
            if not self.client:
                return False
            # Attempt to ping the server to validate the connection
            self.client.admin.command('ping')
            return True
        except ConnectionFailure as e:
            self._handle_exception(e, "MongoDB connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['MONGODB_URI', 'MONGODB_DATABASE']

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> bool:
        """Inserts a document into a specified MongoDB collection."""
        if not self.connected:
            raise ConnectionError("Not connected to MongoDB")

        try:
            collection = self.database[collection_name]
            collection.insert_one(document)
            log.info(f"Successfully inserted document into collection: {collection_name}")
            return True
        except Exception as e:
            self._handle_exception(e, f"Failed to insert document into collection: {collection_name}")
            return False

    def find_documents(self, collection_name: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Finds documents in a specified MongoDB collection based on a query."""
        if not self.connected:
            raise ConnectionError("Not connected to MongoDB")

        try:
            collection = self.database[collection_name]
            results = collection.find(query or {})
            documents = [doc for doc in results]
            log.info(f"Successfully found documents in collection: {collection_name}")
            return documents
        except Exception as e:
            self._handle_exception(e, f"Failed to find documents in collection: {collection_name}")
            return []

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = {"message": f"Notification from {self.name}"}
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False