from logger import log
from components.connectors.excel.excel_connector import ExcelConnector

def main():

    file_name = 'data.xlsx'
    
    excel = ExcelConnector(file_name)

    # List all sheets
    sheets = excel.workbook.sheet_names
    log.info(sheets)
    
    sheet = 'Sheet1'
    excel.read_data(sheet)

    # Get specific cell
    value = excel.get_cell(sheet, 0, 'Nome')
    
    log.info(value)

    # Write new value
    excel.write_cell(sheet, 1, 'Nome', 'Igor Santos')
    excel.write_cell(sheet, 1, 'Sobrenome', 'de Medeiros')


if __name__ == "__main__":
    main()