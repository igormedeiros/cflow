# Conector específico: RestConnector
from cflow.connector import ConnectorBase
from logger import log

class RestConnector(ConnectorBase):
    def __init__(self, name, description=None, base_url=None, endpoint=None, headers=None):
        super().__init__(name, description if description else "Sends POST requests to a REST API")
        self.base_url = base_url
        self.endpoint = endpoint
        self.url = f"{self.base_url}/{self.endpoint}"
        self.headers = headers if headers else {}

    def connect(self):
        log.info(f"Ready to make REST requests to: {self.url}")

    def post(self, payload):
        response = requests.post(self.url, json=payload, headers=self.headers)
        log.info(f"POST to {self.url} with payload {payload} - Status Code: {response.status_code}")
        return response
