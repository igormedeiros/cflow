from fluxr import Flux, Task, Tool, Connector, Trigger
from typing import Any

class CustomTool(Tool):
    async def initialize(self) -> None:
        print(f"Initializing {self.name}")
        
    async def pre_execute(self) -> None:
        print(f"Pre-execute hook: {self.name}")
        
    async def execute(self, input_data: Any) -> Any:
        print(f"Executing {self.name}")
        return input_data
        
    async def post_execute(self) -> None:
        print(f"Post-execute hook: {self.name}")

class CustomConnector(Connector):
    async def initialize(self) -> None:
        print(f"Initializing {self.name}")
        
    async def pre_connect(self) -> None:
        print(f"Pre-connect hook: {self.name}")
        
    async def connect(self) -> None:
        print(f"Connecting {self.name}")
        
    async def post_connect(self) -> None:
        print(f"Post-connect hook: {self.name}")
        
    async def pre_disconnect(self) -> None:
        print(f"Pre-disconnect hook: {self.name}")
        
    async def disconnect(self) -> None:
        print(f"Disconnecting {self.name}")
        
    async def post_disconnect(self) -> None:
        print(f"Post-disconnect hook: {self.name}")

class CustomTrigger(Trigger):
    def __init__(self, name: str = "CustomTrigger"):
        super().__init__(name=name, event_type="custom")
        self._active = False
        
    async def pre_activate(self) -> None:
        print(f"Pre-activate hook: {self.name}")
        
    async def activate(self) -> None:
        print(f"Activating {self.name}")
        self._active = True
        
    async def post_activate(self) -> None:
        print(f"Post-activate hook: {self.name}")
        
    async def pre_deactivate(self) -> None:
        print(f"Pre-deactivate hook: {self.name}")
        
    async def deactivate(self) -> None:
        print(f"Deactivating {self.name}")
        self._active = False
        
    async def post_deactivate(self) -> None:
        print(f"Post-deactivate hook: {self.name}")

class CustomTask(Task):
    async def pre_execute(self) -> None:
        print(f"Pre-execute hook: {self.name}")
        
    async def post_execute(self) -> None:
        print(f"Post-execute hook: {self.name}")

# Create components
tool = CustomTool(name="MyTool")
connector = CustomConnector(name="MyConnector")
trigger = CustomTrigger(name="MyTrigger")

# Create task
task = CustomTask(
    name="MyTask",
    tools=[tool],
    connectors=[connector],
    triggers=[trigger]
)

# Run workflow
flux = Flux(verbose=True, trigger_mode="auto")
flux.add_task(task)
flux.run()