# Task específica que lê de um Excel e faz POST via RestConnector
from cflow.task_base import TaskBase

from logger import log


class ExcelToRestTask(TaskBase):
    def __init__(self, name, description, connectors, tools):
        super().__init__(name, description, connectors=connectors, tools=tools)

    def execute(self):
        log.info(f"Executing task: {self.name} - {self.description}")
        data = self.excel_connector.get_data()
        for index, row in data.iterrows():
            payload = row.to_dict()
            for tool in self.tools:
                payload = tool.execute(payload)
            response = self.rest_connector.post(payload)
            if response.status_code != 200:
                log.error(f"Error: Failed to post data for row {index}, Status Code: {response.status_code}")
