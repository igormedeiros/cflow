# main.py (Implementação de Referência)

from cflow.workflow import Workflow
from connectors.excel.excel_connector import ExcelConnector
from connectors.telegram.telegram_connector import TelegramConnector
from tasks.excel_to_telegram_task import ExcelToTelegramTask


def main():
    # Adicionando conectores
    excel_connector = ExcelConnector(
        name="Excel Connector",
        file_path="data.xlsx"
    )

    telegram_connector = TelegramConnector(
        name="Telegram Notifier",
        token="your_telegram_bot_token",
        chat_id="your_chat_id"
    )

    # Criando a tarefa que lê do Excel e envia os dados pelo Telegram
    excel_to_telegram_task = ExcelToTelegramTask(
        name="Excel to Telegram Task",
        description="Reads data from Excel and sends it to Telegram",
        connectors=[excel_connector, telegram_connector]
    )

    # Criando o workflow
    workflow = Workflow(
        name="Sample Workflow",
        description="This workflow reads data from an Excel file and sends it to a Telegram chat",
        connectors=[
            excel_connector,
            telegram_connector
        ],
        tasks=[excel_to_telegram_task]
    )

    # Executando o workflow
    workflow.run()


if __name__ == "__main__":
    main()
