# Conector específico: ExcelConnector
from cflow.connector import ConnectorBase

import pandas as pd
from logger import log


class ExcelConnector(ConnectorBase):
    def __init__(self, name, description=None, file_path=None):
        super().__init__(name, description if description else "Reads data from an Excel file")
        self.file_path = file_path
        self.data = None

    def connect(self):
        log.info(f"Connecting to Excel file at: {self.file_path}")
        self.data = pd.read_excel(self.file_path)

    def get_data(self):
        return self.data
