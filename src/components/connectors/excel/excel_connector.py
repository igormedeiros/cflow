import pandas as pd
from logger import log
from components.connectors.base_connector import BaseConnector

class ExcelConnector(BaseConnector):
   def __init__(self, file_path):
       self.file_path = file_path
       self.workbook = pd.ExcelFile(file_path)

   def read_data(self, sheet_name=0):
       """
       Read data from Excel file
       sheet_name: sheet name or index (default: 0)
       returns: pandas DataFrame or None if error
       """
       try:
           data = pd.read_excel(self.workbook, sheet_name=sheet_name)
           log.info(f"Successfully read data from sheet '{sheet_name}'")
           return data
       except Exception as e:
           log.error(f"Error reading Excel file: {e}")
           return None

   def get_cell(self, sheet_name, row, col):
       """
       Get specific cell value
       sheet_name: sheet name or index
       row: row number (starting from 1)
       col: column number or name
       returns: cell value or None if error
       """
       try:
           data = pd.read_excel(self.workbook, sheet_name=sheet_name)
           # Adjust row index for pandas (subtract 1 as Excel starts from 1)
           row_idx = row - 1
           value = data.iloc[row_idx, col] if isinstance(col, int) else data.loc[row_idx, col]
           log.info(f"Successfully retrieved value from sheet '{sheet_name}' [{row}, {col}]")
           return value
       except Exception as e:
           log.error(f"Error accessing cell in sheet '{sheet_name}' [{row}, {col}]: {e}")
           return None

   def write_cell(self, sheet_name, row, col, value):
       """
       Write value to specific cell
       sheet_name: sheet name or index
       row: row number (starting from 1)
       col: column number or name
       value: new value to write
       """
       try:
           data = pd.read_excel(self.file_path, sheet_name=sheet_name)
           # Adjust row index for pandas (subtract 1 as Excel starts from 1)
           row_idx = row - 1
           if isinstance(col, int):
               data.iloc[row_idx, col] = value
           else:
               data.loc[row_idx, col] = value
           
           with pd.ExcelWriter(self.file_path, mode='w') as writer:
               data.to_excel(writer, sheet_name=sheet_name, index=False)
           log.info(f"Successfully wrote value to sheet '{sheet_name}' [{row}, {col}]")
       except Exception as e:
           log.error(f"Error writing to cell in sheet '{sheet_name}' [{row}, {col}]: {e}")

   def get_sheets(self):
       """
       Get list of sheet names
       returns: list of sheet names
       """
       return self.workbook.sheet_names