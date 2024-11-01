# main.py (Implementação de Referência)

from src.cflow.workflow import Workflow
from src.cflow.connector import ExcelConnector, RestConnector, TelegramConnector
from src.cflow.task import ExcelToRestTask
from src.cflow.tool import UpperCaseTool

if __name__ == "__main__":
    workflow = Workflow(name="Sample Workflow", description="This workflow reads data from an Excel file and sends it to a REST API")
    
    # Adicionando conectores
    excel_connector = ExcelConnector(name="Excel Connector", file_path="path/to/excel/file.xlsx")
    rest_connector = RestConnector(name="REST API Connector", base_url="https://example.com", endpoint="api/endpoint")
    telegram_connector = TelegramConnector(name="Telegram Notifier", token="your_telegram_bot_token", chat_id="your_chat_id")
    
    workflow.add_connector(excel_connector)
    workflow.add_connector(rest_connector)
    workflow.add_connector(telegram_connector)
    
    # Criando a tarefa que lê do Excel e faz POST para a API REST
    excel_to_rest_task = ExcelToRestTask(name="Excel to REST Task", description="Reads data from Excel and posts to REST API", excel_connector=excel_connector, rest_connector=rest_connector)
    
    # Adicionando a ferramenta de transformação à tarefa
    uppercase_tool = UpperCaseTool()
    excel_to_rest_task.add_tool(uppercase_tool)
    
    # Adicionando a tarefa ao workflow
    workflow.add_task(excel_to_rest_task)

    # Executando o workflow
    workflow.run()
