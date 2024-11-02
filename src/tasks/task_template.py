# File: src/tasks/task_template.py
from src.cflow.task_base import TaskBase
from logger import log

class TaskTemplate(TaskBase):
    def __init__(self, name="TaskTemplate", description=None, connectors=None, tools=None, retry_attempts: int = 3):
        """
        Initializes a template for creating new tasks.
        :param name: Name of the task.
        :param description: Optional description of the task.
        :param connectors: Optional list of connectors to be used in the task.
        :param tools: Optional list of tools to be used in the task.
        :param retry_attempts: Number of retry attempts in case of failure.
        """
        super().__init__(name, description if description else "Template task for developers to extend", connectors, tools, retry_attempts)

    def execute(self) -> None:
        """
        Execute the task.
        """
        log.info(f"Executing {self.name}")
        if not self.validate():
            log.error(f"Task validation failed for: {self.name}")
            return

        self.pre_execute_hook()
        # Task-specific logic here
        try:
            log.info("Running the main logic of the task.")
            # Example: Loop through connectors and perform specific operations
            for connector in self.connectors:
                connector.connect()
                # Example operation
            for tool in self.tools:
                tool.run()
        except Exception as e:
            log.error(f"An error occurred while executing {self.name}: {e}")
        finally:
            # Ensure connectors are disconnected after execution
            for connector in self.connectors:
                connector.disconnect()

        self.post_execute_hook()

    def pre_execute_hook(self) -> None:
        """
        Hook to execute operations before the main task logic.
        Can be customized by extending the class.
        """
        log.info(f"Running pre-execute hook for task: {self.name}")

    def post_execute_hook(self) -> None:
        """
        Hook to execute operations after the main task logic.
        Can be customized by extending the class.
        """
        log.info(f"Running post-execute hook for task: {self.name}")