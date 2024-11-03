# File: kubernetes_connector.py
import os
from typing import Optional, List, Dict, Any
from kubernetes import client, config
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.logger import log


class KubernetesConnector(ConnectorBase, NotifiableConnector):
    def __init__(
            self,
            name: str = "KubernetesConnector",
            description: Optional[str] = None,
            kube_config_path: Optional[str] = None,
            retry_attempts: int = 3,
            timeout: int = 30,
            enable_retry: bool = True
    ):
        """
        Initializes the Kubernetes Connector instance.
        """
        super().__init__(
            name=name,
            description=description or "Connector for Kubernetes cluster integration",
            retry_attempts=retry_attempts,
            timeout=timeout,
            enable_retry=enable_retry
        )
        self.kube_config_path = kube_config_path or os.getenv('KUBECONFIG')
        self.core_v1_api = None

        if not self.kube_config_path:
            raise ValueError("Kubeconfig path must be provided for KubernetesConnector.")

    def connect(self, **kwargs) -> None:
        """Establishes connection to Kubernetes cluster."""
        try:
            self.pre_connect_hook(kwargs)
            self.validate_parameters(kwargs)
            config.load_kube_config(config_file=self.kube_config_path)
            self.core_v1_api = client.CoreV1Api()
            if self.validate_connection():
                self.connected = True
                log.info("Successfully connected to Kubernetes cluster")
                self.post_connect_hook()
            else:
                raise ConnectionError("Failed to validate Kubernetes cluster connection")

        except Exception as e:
            self._handle_exception(e, "Failed to connect to Kubernetes cluster")
            raise

    def validate_connection(self) -> bool:
        """Validates if Kubernetes connection is successful by listing namespaces."""
        try:
            namespaces = self.core_v1_api.list_namespace()
            log.info(f"Kubernetes connection validated successfully. Found namespaces: {[ns.metadata.name for ns in namespaces.items]}")
            return True
        except Exception as e:
            self._handle_exception(e, "Kubernetes connection validation failed")
            return False

    def disconnect(self) -> None:
        """Disconnects from Kubernetes cluster by cleaning up resources."""
        try:
            log.info("Disconnecting from Kubernetes cluster")
            self.connected = False
            self.core_v1_api = None
        except Exception as e:
            self._handle_exception(e, "Error during Kubernetes cluster disconnection")
            raise

    def list_pods(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Lists pods in a specified namespace."""
        if not self.connected:
            raise ConnectionError("Not connected to Kubernetes cluster")

        try:
            pods = self.core_v1_api.list_namespaced_pod(namespace=namespace)
            log.info(f"Successfully listed pods in namespace '{namespace}'")
            return [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pods.items]
        except Exception as e:
            self._handle_exception(e, f"Failed to list pods in namespace '{namespace}'")
            raise

    def create_namespace(self, namespace: str) -> None:
        """Creates a namespace in the Kubernetes cluster."""
        if not self.connected:
            raise ConnectionError("Not connected to Kubernetes cluster")

        try:
            body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
            self.core_v1_api.create_namespace(body=body)
            log.info(f"Successfully created namespace '{namespace}' in Kubernetes cluster")
        except Exception as e:
            self._handle_exception(e, f"Failed to create namespace '{namespace}' in Kubernetes cluster")
            raise

    def delete_namespace(self, namespace: str) -> None:
        """Deletes a namespace in the Kubernetes cluster."""
        if not self.connected:
            raise ConnectionError("Not connected to Kubernetes cluster")

        try:
            self.core_v1_api.delete_namespace(name=namespace)
            log.info(f"Successfully deleted namespace '{namespace}' in Kubernetes cluster")
        except Exception as e:
            self._handle_exception(e, f"Failed to delete namespace '{namespace}' in Kubernetes cluster")
            raise

    def get_env_keys(self) -> List[str]:
        """Provides the list of environment variable keys required for Kubernetes connection."""
        return ['KUBECONFIG']

    def notify(self, message: str = None) -> bool:
        """Implementation of NotifiableConnector interface."""
        try:
            default_message = f"Notification from {self.name}"
            log.info(default_message if not message else message)
            return True
        except Exception as e:
            log.error(f"Failed to send notification: {str(e)}")
            return False