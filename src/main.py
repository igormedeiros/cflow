# main.py (Implementação de Referência)

from cflow.workflow import Workflow
from connectors.excel_connector import ExcelConnector
from connectors.rest_connector import RestConnector
from connectors.telegram_connector import TelegramConnector
from tasks.excel_to_rest_task import ExcelToRestTask
from tools.upercase_tool import UpperCaseTool


def main():
    # Adicionando conectores
    excel_connector = ExcelConnector(
        name="Excel Connector",
        file_path="data.xlsx"
    )
    rest_connector = RestConnector(
        name="REST API Connector",
        base_url="https://example.com",
        endpoint="api/endpoint"
    )

    telegram_connector = TelegramConnector(name="Telegram Notifier", token="your_telegram_bot_token",
                                           chat_id="your_chat_id")

    uppercase_tool = UpperCaseTool()

    # Criando a tarefa que lê do Excel e faz POST para a API REST
    excel_to_rest_task = ExcelToRestTask(
        name="Excel to REST Task",
        description="Reads data from Excel and posts to REST API",
        connectors=[excel_connector, rest_connector],
        tools=[uppercase_tool]
    )

    workflow = Workflow(
        name="Sample Workflow",
        description="This workflow reads data from an Excel file and sends it to a REST API",
        connectors=[
            excel_connector,
            rest_connector,
            telegram_connector
        ],
        tasks=[excel_to_rest_task]
    )

    # Executando o workflow
    workflow.run()


if __name__ == "__main__":
    main()
