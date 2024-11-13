from typing import Any
from fluxr import Flux, Task, Tool

class DataTransformTool(Tool):
    def __init__(self, name: str = "DataTransformTool"):
        super().__init__(name=name, description="Transform data using custom logic")
        
    async def initialize(self) -> None:
        """Initialize the tool."""
        pass
        
    async def execute(self, input_data: Any) -> Any:
        """Transform input data."""
        if isinstance(input_data, list):
            # Example: Calculate average of numeric values
            numeric_values = [x for x in input_data if isinstance(x, (int, float))]
            if numeric_values:
                return sum(numeric_values) / len(numeric_values)
        return input_data

# Create task with custom tool
task = Task(
    name="DataTransformTask",
    tools=[DataTransformTool()]
)

# Run workflow
flux = Flux(verbose=True)
flux.add_task(task)
flux.run()