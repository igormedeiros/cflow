from componnents.connectors.base_connector import BaseConnector
import json

class JSONConnector(BaseConnector):
    def connect(self, file_path):
        print("Connecting to JSON data source")

        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def disconnect(self):
        print("Disconnecting from JSON data source")

# Exemplo de uso
if __name__ == "__main__":
    connector = JSONConnector()
    connector.connect()
    connector.disconnect()