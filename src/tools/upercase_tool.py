# Tool específica que transforma os valores em maiúsculas
from cflow.tool import ToolBase


class UpperCaseTool(ToolBase):
    def __init__(self, name="Uppercase Tool", description="Transforms data to uppercase"):
        super().__init__(name, description)

    def execute(self, data):
        log.info(f"Executing tool: {self.name}")
        return {key: str(value).upper() for key, value in data.items()}
