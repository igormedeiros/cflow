# File: jira_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class JiraConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "JiraConnector",
            description: Optional[str] = None,
            base_url: Optional[str] = None,
            username: Optional[str] = None,
            api_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the JiraConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Jira integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.base_url = base_url or os.getenv('JIRA_BASE_URL')
        self.username = username or os.getenv('JIRA_USERNAME')
        self.api_token = api_token or os.getenv('JIRA_API_TOKEN')
        self.headers = {
            "Authorization": f"Basic {requests.auth._basic_auth_str(self.username, self.api_token)}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with Jira API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Jira API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Jira connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Jira")
            raise

    def disconnect(self) -> None:
        """Disconnects from Jira API."""
        try:
            log.info("Disconnecting from Jira API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during Jira disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to Jira API."""
        try:
            if not self.base_url or not self.username or not self.api_token:
                return False
            url = f"{self.base_url}/rest/api/3/myself"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "Jira connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['JIRA_BASE_URL', 'JIRA_USERNAME', 'JIRA_API_TOKEN']

    def create_issue(self, project_key: str, summary: str, issue_type: str, description: Optional[str] = None) -> bool:
        """Creates a new issue in the specified Jira project."""
        if not self.connected:
            raise ConnectionError("Not connected to Jira API")

        try:
            url = f"{self.base_url}/rest/api/3/issue"
            payload = {
                "fields": {
                    "project": {
                        "key": project_key
                    },
                    "summary": summary,
                    "description": description or "",
                    "issuetype": {
                        "name": issue_type
                    }
                }
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created issue in Jira project: {project_key}")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create issue in Jira")
            return False

    def get_issues(self, jql_query: str) -> List[Dict[str, Any]]:
        """Gets issues from Jira based on the provided JQL query."""
        if not self.connected:
            raise ConnectionError("Not connected to Jira API")

        try:
            url = f"{self.base_url}/rest/api/3/search"
            params = {"jql": jql_query}
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            issues = response.json().get('issues', [])
            log.info(f"Successfully retrieved issues from Jira")
            return issues
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve issues from Jira")
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