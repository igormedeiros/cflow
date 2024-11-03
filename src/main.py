import os
from dotenv import load_dotenv
from cflow.workflow import Workflow
from connectors.excel.excel_connector import ExcelConnector
from connectors.telegram.telegram_connector import TelegramConnector
from cflow.task_protocol import TaskProtocol
from cflow.logger import log
from tasks.excel_to_telegram_task import ExcelToTelegramTask


def main():
    log.info("=== Initializing Workflow ===")
    load_dotenv()

    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    # Logs com mascaramento de dados sensíveis
    masked_token = f"{'*' * 10}{token[-5:]}" if token else "Not found"
    log.info(f"Environment loaded - TELEGRAM_BOT_TOKEN: {masked_token}")
    log.info(f"Environment loaded - TELEGRAM_CHAT_ID: {chat_id or 'Not found'}")

    try:
        # Configurando conectores
        excel_connector = ExcelConnector(
            name="Excel Data Source",
            file_path="data.xlsx"
        )

        telegram_connector = TelegramConnector(
            name="Telegram Notifier",
            token=token,
            chat_id=chat_id,
            parse_mode="HTML"
        )

        # Criando a tarefa
        excel_to_telegram_task = ExcelToTelegramTask(
            name="Excel to Telegram Task",
            description="Reads data from Excel and sends it to Telegram",
            connectors=[excel_connector, telegram_connector]
        )

        # Criando o workflow
        workflow = Workflow(
            name="Excel to Telegram Workflow",
            description="Workflow for processing Excel data and sending via Telegram",
            connectors=[excel_connector, telegram_connector],
            tasks=[excel_to_telegram_task]
        )

        # Executando o workflow
        workflow.run()
        log.info("Workflow executed successfully")

    except Exception as e:
        log.error(f"Workflow execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()