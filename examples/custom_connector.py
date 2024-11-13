from typing import Any, Dict
import json
from fluxr import Flux, Task, Connector

class JSONFileConnector(Connector):
    def __init__(self, name: str = "JSONFileConnector"):
        super().__init__(
            name=name,
            description="Read and write JSON files"
        )
        self.file_path = None
        
    async def initialize(self) -> None:
        """Initialize the JSON file connector."""
        self.file_path = self.connection_params.get("file_path")
        if not self.file_path:
            raise ValueError("JSON file path not provided")
        
    async def connect(self) -> None:
        """Verify JSON file exists."""
        try:
            with open(self.file_path, 'r') as f:
                json.load(f)
        except FileNotFoundError:
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
                
    async def disconnect(self) -> None:
        """No cleanup needed for JSON files."""
        pass
        
    async def read_data(self) -> Dict[str, Any]:
        """Read data from JSON file."""
        with open(self.file_path, 'r') as f:
            return json.load(f)
            
    async def write_data(self, data: Dict[str, Any]) -> None:
        """Write data to JSON file."""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

# Create task with custom connector
json_connector = JSONFileConnector()
json_connector.connection_params = {
    "file_path": "data/config.json"
}

task = Task(
    name="JSONProcessingTask",
    connectors=[json_connector]
)

# Run workflow
flux = Flux(verbose=True)
flux.add_task(task)
flux.run()