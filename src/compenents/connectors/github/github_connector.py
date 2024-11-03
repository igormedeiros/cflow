# File: github_connector.py
import os
from typing import Optional, List, Dict, Any
import requests
from core.connector.connector_base import ConnectorBase, NotifiableConnector
from core.logger import log


class GitHubConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "GitHubConnector",
            description: Optional[str] = None,
            repository: Optional[str] = None,
            personal_access_token: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the GitHubConnector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for GitHub integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.repository = repository or os.getenv('GITHUB_REPOSITORY')
        self.personal_access_token = personal_access_token or os.getenv('GITHUB_PAT')
        self.base_url = f"https://api.github.com/repos/{self.repository}"
        self.headers = {
            "Authorization": f"Bearer {self.personal_access_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }

    def connect(self, **kwargs) -> None:
        """Establishes connection with GitHub API."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            self._load_credentials()
            self._validate_credentials()

            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to GitHub API")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate GitHub connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to GitHub")
            raise

    def disconnect(self) -> None:
        """Disconnects from GitHub API."""
        try:
            log.info("Disconnecting from GitHub API")
            self.connected = False
        except Exception as e:
            self._handle_exception(e, "Error during GitHub disconnection")
            raise

    def validate_connection(self) -> bool:
        """Validates the connection to GitHub API."""
        try:
            if not self.repository or not self.personal_access_token:
                return False
            url = f"{self.base_url}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            self._handle_exception(e, "GitHub connection validation failed")
            return False

    def get_env_keys(self) -> List[str]:
        """Returns required environment variable keys."""
        return ['GITHUB_REPOSITORY', 'GITHUB_PAT']

    def create_issue(self, title: str, body: Optional[str] = None, labels: Optional[List[str]] = None) -> bool:
        """Creates a new issue in the specified GitHub repository."""
        if not self.connected:
            raise ConnectionError("Not connected to GitHub API")

        try:
            url = f"{self.base_url}/issues"
            payload = {
                "title": title,
                "body": body or "",
                "labels": labels or []
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            log.info(f"Successfully created issue in GitHub repository: {title}")
            return True
        except Exception as e:
            self._handle_exception(e, "Failed to create issue in GitHub")
            return False

    def get_issues(self, state: str = "open") -> List[Dict[str, Any]]:
        """Gets issues from the specified GitHub repository."""
        if not self.connected:
            raise ConnectionError("Not connected to GitHub API")

        try:
            url = f"{self.base_url}/issues"
            params = {"state": state}
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            issues = response.json()
            log.info(f"Successfully retrieved issues from GitHub repository")
            return issues
        except Exception as e:
            self._handle_exception(e, "Failed to retrieve issues from GitHub")
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