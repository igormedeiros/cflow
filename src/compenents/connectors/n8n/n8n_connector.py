# File: n8n_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class N8NConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "N8NConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            api_key: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the N8NConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for N8N integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('N8N_BASE_URL', 'https://n8n.example.com')
        self.api_key = api_key or os.getenv('N8N_API_KEY')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with N8N API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to N8N API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate N8N connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to N8N")
            raise

    def disconnect(self) -> None:
        """Disconnects from N8N API."""
        try:
            log.info("Disconnecting from N8N API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during N8N disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to N8N API."""
        try:
            if not self.base_url or not self.api_key:
                return False
            url = f"{self.base_url}/rest/healthz"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "N8N connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['N8N_BASE_URL', 'N8N_API_KEY']

    def trigger_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Triggers a workflow in N8N by its ID."""
        if not self.connected:
            raise ConnectionError("Not connected to N8N API")

        try:
            url = f"{self.base_url}/webhook/{workflow_id}"
            response = requests.post(url, json=data or {}, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully triggered workflow ID: {workflow_id}")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to trigger workflow ID: {workflow_id}")
            return {}

    def get_workflows(self) -> List[Dict[str, Any]]:
        """Gets a list of all workflows from N8N."""
        if not self.connected:
            raise ConnectionError("Not connected to N8N API")

        try:
            url = f"{self.base_url}/rest/workflows"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            workflows = response.json()
            log.info("Successfully retrieved workflows from N8N")
            return workflows.get('data', [])
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve workflows from N8N")
            return []

    def get_workflow_details(self, workflow_id: str) -> Dict[str, Any]:
        """Gets the details of a specific workflow by its ID."""
        if not self.connected:
            raise ConnectionError("Not connected to N8N API")

        try:
            url = f"{self.base_url}/rest/workflows/{workflow_id}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            workflow_details = response.json()
            log.info(f"Successfully retrieved details for workflow ID: {workflow_id}")
            return workflow_details
        except Exception as e:
            self._handle_exception(e, f"Failed to retrieve workflow details for ID: {workflow_id}")
            return {}

    def execute_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a specific workflow directly by its ID."""
        if not self.connected:
            raise ConnectionError("Not connected to N8N API")

        try:
            url = f"{self.base_url}/rest/workflows/{workflow_id}/executions"
            response = requests.post(url, json=data or {}, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully executed workflow ID: {workflow_id}")
            return response.json()
        except Exception as e:
            self._handle_exception(e, f"Failed to execute workflow ID: {workflow_id}")
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