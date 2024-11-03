# File: src/cflow/task_base.py
from cflow.task_protocol import TaskProtocol
from cflow.logger import log
import time
import random

class TaskBase(TaskProtocol):
    def __init__(self, name: str, description: str = None, connectors=None, tools=None, retry_attempts: int = 3, backoff_factor: float = 1.5):
        """
        Initializes a base task with given parameters.

        :param name: Name of the task.
        :param description: Optional description of the task.
        :param connectors: Optional list of connectors to be used in the task.
        :param tools: Optional list of tools to be used in the task.
        :param retry_attempts: Number of retry attempts in case of failure.
        :param backoff_factor: Factor to apply exponential backoff delay between retries.

        Example:
            task = TaskBase(name="MyTask", description="Example Task", retry_attempts=2)
        """
        self.name = name
        self.description = description if description else "No description provided."
        self.connectors = connectors if connectors else []
        self.tools = tools if tools else []
        self.retry_attempts = retry_attempts
        self.backoff_factor = backoff_factor
        self.state = "initialized"

    def add_tool(self, tool):
        """
        Adds a tool to the task.
        :param tool: The tool to add.

        Example:
            task.add_tool(my_tool)
        """
        self.tools.append(tool)

    def add_connector(self, connector):
        """
        Adds a connector to the task.
        :param connector: The connector to add.

        Example:
            task.add_connector(my_connector)
        """
        self.connectors.append(connector)

    def validate(self) -> bool:
        """
        Validate the task by ensuring connectors and tools are available.
        :return: Boolean indicating if the task setup is valid.

        Example:
            is_valid = task.validate()
        """
        log.info(f"Validating task: {self.name}")
        if not self.connectors:
            log.error("No connectors found for the task.")
            self.state = "validation_failed"
            return False
        return True

    def pre_execute_hook(self) -> None:
        """
        Hook to execute operations before the main task logic.

        Example:
            task.pre_execute_hook()
        """
        log.info(f"Running pre-execute hook for task: {self.name}")

    def post_execute_hook(self) -> None:
        """
        Hook to execute operations after the main task logic.

        Example:
            task.post_execute_hook()
        """
        log.info(f"Running post-execute hook for task: {self.name}")

    def _retry_logic(self, attempt: int) -> None:
        """
        Implements retry logic with exponential backoff.

        :param attempt: Current retry attempt number.
        """
        delay = self.backoff_factor ** attempt
        log.info(f"Retrying task {self.name} in {delay:.2f} seconds...")
        time.sleep(delay)

    def execute(self) -> None:
        """
        Execute the task.

        Example:
            task.execute()
        """
        log.info(f"Starting execution of task: {self.name}")
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
                self._run_connectors()
                self._run_tools()
                self.post_execute_hook()
                self.state = "completed"
                log.info(f"Task {self.name} completed successfully.")
                break
            except Exception as e:
                attempt += 1
                self.state = "retrying"
                log.error(f"An error occurred while executing {self.name} (Attempt {attempt}/{self.retry_attempts}): {e}")
                if attempt >= self.retry_attempts:
                    self.state = "failed"
                    log.error(f"Task {self.name} failed after {self.retry_attempts} attempts.")
                else:
                    self._retry_logic(attempt)

        if self.state == "failed":
            log.error(f"Final state of task {self.name}: {self.state}")
        else:
            log.info(f"Final state of task {self.name}: {self.state}")

    def _run_connectors(self) -> None:
        """
        Run all connectors by establishing their respective connections.
        """
        for connector in self.connectors:
            try:
                connector.connect()
            except Exception as e:
                log.error(f"Failed to connect using {connector}: {e}")
                raise

    def _run_tools(self) -> None:
        """
        Run all tools associated with the task.
        """
        for tool in self.tools:
            try:
                tool.run()
            except Exception as e:
                log.error(f"Failed to run tool {tool}: {e}")
                raise
