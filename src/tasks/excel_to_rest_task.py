# Task específica que lê de um Excel e faz POST via RestConnector
class ExcelToRestTask(TaskBase):
    def __init__(self, name, description, excel_connector, rest_connector):
        super().__init__(name, description, connectors=[excel_connector, rest_connector])
        self.excel_connector = excel_connector
        self.rest_connector = rest_connector

    def execute(self):
        print(f"Executing task: {self.name} - {self.description}")
        data = self.excel_connector.get_data()
        for index, row in data.iterrows():
            payload = row.to_dict()
            for tool in self.tools:
                payload = tool.execute(payload)
            response = self.rest_connector.post(payload)
            if response.status_code != 200:
                print(f"Error: Failed to post data for row {index}, Status Code: {response.status_code}")
