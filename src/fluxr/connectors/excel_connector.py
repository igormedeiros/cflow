from typing import Dict, Any
import openpyxl
from ..base import Connector

class ExcelConnector(Connector):
    def __init__(self, name: str = "ExcelConnector"):
        super().__init__(name=name)
        self.workbook = None
        
    async def initialize(self) -> None:
        """Initialize the Excel connector."""
        pass
        
    async def connect(self) -> None:
        """Connect to Excel file."""
        file_path = self.connection_params.get("file_path")
        if not file_path:
            raise ValueError("Excel file path not provided")
        self.workbook = openpyxl.load_workbook(file_path)
        
    async def disconnect(self) -> None:
        """Close Excel file."""
        if self.workbook:
            self.workbook.close()
            
    async def read_worksheet(self, sheet_name: str) -> List[Dict[str, Any]]:
        """Read data from worksheet."""
        if not self.workbook:
            raise RuntimeError("Not connected to Excel file")
            
        worksheet = self.workbook[sheet_name]
        headers = [cell.value for cell in worksheet[1]]
        
        data = []
        for row in worksheet.iter_rows(min_row=2):
            row_data = {}
            for header, cell in zip(headers, row):
                row_data[header] = cell.value
            data.append(row_data)
            
        return data