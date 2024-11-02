# File: src/tasks/excel_to_telegram_task.py
from src.cflow.task_base import TaskBase
from logger import log


class ExcelToTelegramTask(TaskBase):
    def __init__(self, name="ExcelToTelegramTask", description=None, connectors=None, tools=None,
                 retry_attempts: int = 3, backoff_factor: float = 1.5):
        """
        Initializes the Excel to Telegram Task.
        :param name: Name of the task.
        :param description: Optional description of the task.
        :param connectors: Optional list of connectors to be used in the task.
        :param tools: Optional list of tools to be used in the task.
        :param retry_attempts: Number of retry attempts in case of failure.
        :param backoff_factor: Factor to apply exponential backoff delay between retries.

        Example:
            connectors = [ExcelConnector(), TelegramConnector()]
            task = ExcelToTelegramTask(connectors=connectors)
        """
        super().__init__(name, description if description else "Reads from Excel and sends data via Telegram",
                         connectors, tools, retry_attempts, backoff_factor)

    def execute(self) -> None:
        """
        Execute the task by reading data from Excel and sending it via Telegram.

        Example:
            task.execute()
        """
        log.info(f"Starting execution of {self.name}")
        self.state = "starting"
        if not self.validate():
            log.error(f"Task validation failed for: {self.name}")
            return

        attempt = 0
        while attempt < self.retry_attempts:
            try:
                self.state = "running"
                log.info(f"Task {self.name} is running. (Attempt {attempt + 1}/{self.retry_attempts})")
                self.pre_execute_hook()
                self._read_from_excel_and_send_to_telegram()
                self.post_execute_hook()
                self.state = "completed"
                log.info(f"Task {self.name} completed successfully.")
                break
            except Exception as e:
                attempt += 1
                self.state = "retrying"
                log.error(
                    f"An error occurred while executing {self.name} (Attempt {attempt}/{self.retry_attempts}): {e}")
