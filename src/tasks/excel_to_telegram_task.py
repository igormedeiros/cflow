# File: src/tasks/excel_to_telegram_task.py
from cflow.task_protocol import TaskProtocol
from cflow.logger import log
from connectors.excel.excel_connector import ExcelConnector
from connectors.telegram.telegram_connector import TelegramConnector


class ExcelToTelegramTask(TaskProtocol):
    def __init__(self, name: str, description: str, connectors: list):
        self.name = name
        self.description = description
        self.connectors = connectors
        self.excel_connector = connectors[0]
        self.telegram_connector = connectors[1]

    def validate(self) -> bool:
        try:
            if len(self.connectors) != 2:
                log.error("Task requires exactly 2 connectors (Excel and Telegram)")
                return False

            if not isinstance(self.excel_connector, ExcelConnector):
                log.error("First connector must be ExcelConnector")
                return False

            if not isinstance(self.telegram_connector, TelegramConnector):
                log.error("Second connector must be TelegramConnector")
                return False

            return True
        except Exception as e:
            log.error(f"Task validation failed: {str(e)}")
            return False

    def pre_execute_hook(self) -> None:
        log.info(f"Starting task: {self.name}")
        for connector in self.connectors:
            if not connector.connected:
                connector.connect()

    def execute(self) -> None:
        try:
            # Lê dados do Excel
            excel_data = self.excel_connector.get_data()
            if excel_data.empty:
                raise ValueError("No data received from Excel")

            # Envia para o Telegram
            success = self.telegram_connector.send_data(excel_data)
            if not success:
                raise RuntimeError("Failed to send data to Telegram")

            log.info("Successfully processed and sent Excel data to Telegram")

        except Exception as e:
            log.error(f"Task execution failed: {str(e)}")
            raise

    def post_execute_hook(self) -> None:
        log.info(f"Completed task: {self.name}")
