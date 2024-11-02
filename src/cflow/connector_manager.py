import pkg_resources
from logger import log

class ConnectorManager:
    def __init__(self):
        self.connectors = {}
        self.load_connectors()

    def load_connectors(self):
        """
        Auto-discover and load available connectors using entry points.
        """
        log.info("Loading connectors using auto-discovery...")
        for entry_point in pkg_resources.iter_entry_points('cflow.connectors'):
            try:
                connector_class = entry_point.load()
                self.connectors[entry_point.name] = connector_class
                log.info(f"Loaded connector: {entry_point.name}")
            except Exception as e:
                log.error(f"Failed to load connector {entry_point.name}: {e}")

    def get_connector(self, name, **kwargs):
        """
        Retrieve a connector by name.
        :param name: The name of the connector.
        :param kwargs: Additional parameters to pass to the connector constructor.
        :return: An instance of the requested connector.
        """
        connector_class = self.connectors.get(name)
        if not connector_class:
            raise ValueError(f"Connector '{name}' not found.")
        return connector_class(**kwargs)
