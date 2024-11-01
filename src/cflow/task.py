# src/cflow/task.py

class TaskBase:
    def __init__(self, name, description=None, connectors=None, tools=None):
        self.name = name
        self.description = description
        self.connectors = connectors if connectors else []
        self.tools = tools if tools else []

    def add_tool(self, tool):
        self.tools.append(tool)

    def add_connector(self, connector):
        self.connectors.append(connector)

    def execute(self):
        print(f"Executing task: {self.name}")
        for connector in self.connectors:
            connector.connect()
        for tool in self.tools:
            tool.run()
