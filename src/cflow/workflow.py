# src/cflow/workflow.py

class Workflow:
    def __init__(self, name, description=None, tools=None, connectors=None):
        self.name = name
        self.description = description
        self.tasks = []
        self.connectors = connectors if connectors else []
        self.tools = tools if tools else []

    def add_task(self, task):
        self.tasks.append(task)

    def add_connector(self, connector):
        self.connectors.append(connector)

    def run(self):
        for connector in self.connectors:
            connector.connect()
        for task in self.tasks:
            task.execute()
        for connector in self.connectors:
            if hasattr(connector, 'notify'):
                connector.notify()
