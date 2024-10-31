class BaseConnector:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.connected = False

    def connect(self):
        """Establish a connection."""
        if not self.connected:
            self.connected = True
            print(f"{self.name} v{self.version} connected.")
        else:
            print(f"{self.name} v{self.version} is already connected.")

    def disconnect(self):
        """Terminate the connection."""
        if self.connected:
            self.connected = False
            print(f"{self.name} v{self.version} disconnected.")
        else:
            print(f"{self.name} v{self.version} is not connected.")

    def status(self):
        """Return the connection status."""
        return "Connected" if self.connected else "Disconnected"