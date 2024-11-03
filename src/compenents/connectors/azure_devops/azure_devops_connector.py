# File: azure_devops_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class AzureDevOpsConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "AzureDevOpsConnector",
            description: Optional[str] = None,
            organization: Optional[str] = None,
            project: Optional[str] = None,
            personal_access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the AzureDevOpsConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Azure DevOps integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.organization = organization or os.getenv('AZURE_DEVOPS_ORGANIZATION')
        self.project = project or os.getenv('AZURE_DEVOPS_PROJECT')
        self.personal_access_token = personal_access_token or os.getenv('AZURE_DEVOPS_PAT')
        self.base_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.auth = ("", self.personal_access_token)

    def connect(self, **kwargs) -> None:
        """Establishes connection with Azure DevOps API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Azure DevOps API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Azure DevOps connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Azure DevOps")
            raise

    def disconnect(self) -> None:
        """Disconnects from Azure DevOps API."""
        try:
            log.info("Disconnecting from Azure DevOps API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Azure DevOps disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Azure DevOps API."""
        try:
            if not self.organization or not self.project or not self.personal_access_token:
                return False
            url = f"{self.base_url}/projects?api-version=6.0"
            response = requests.get(url, auth=self.auth, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Azure DevOps connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['AZURE_DEVOPS_ORGANIZATION', 'AZURE_DEVOPS_PROJECT', 'AZURE_DEVOPS_PAT']

    def create_work_item(self, work_item_type: str, title: str, fields: Dict[str, Any]) -> bool:
        """Creates a new work item in Azure DevOps."""
        if not self.connected:
            raise ConnectionError("Not connected to Azure DevOps API")

        try:
            url = f"{self.base_url}/wit/workitems/${work_item_type}?api-version=6.0"
            payload = [
                {"op": "add", "path": "/fields/System.Title", "value": title}
            ]
            for key, value in fields.items():
                payload.append({"op": "add", "path": f"/fields/{key}", "value": value})

            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created work item in Azure DevOps: {title}")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create work item in Azure DevOps")
            return False

    def get_work_items(self, query: str) -> List[Dict[str, Any]]:
        """Queries work items from Azure DevOps based on the provided query string."""
        if not self.connected:
            raise ConnectionError("Not connected to Azure DevOps API")

        try:
            url = f"{self.base_url}/wit/wiql?api-version=6.0"
            payload = {"query": query}
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            work_items = response.json().get('workItems', [])
            log.info("Successfully retrieved work items from Azure DevOps")
            return work_items
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve work items from Azure DevOps")
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