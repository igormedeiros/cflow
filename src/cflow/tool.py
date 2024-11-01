# src/cflow/tool.py

class ToolBase:
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def execute(self, data):
        raise NotImplementedError("The execute method must be implemented by subclasses")
