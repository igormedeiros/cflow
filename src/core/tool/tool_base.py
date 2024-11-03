# File: src/core/tool_base.py
import time
from enum import Enum
from core.logger import log
from core.tool.tool_protocol import ToolProtocol

class ToolState(Enum):
    INIT = "Initialized"
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILED = "Failed"

class ToolBase(ToolProtocol):
    def __init__(self, name: str, description: str = None, max_retries: int = 3, backoff_factor: float = 2.0):
        """
        Initializes the base tool with the given name, description, and retry settings.

        :param name: Name of the tool.
        :param description: Optional description of the tool.
        :param max_retries: Maximum number of retries in case of failure.
        :param backoff_factor: Factor by which the wait time increases with each retry.

        Example:
            tool = ToolBase(name="MyTool", description="An example tool", max_retries=3, backoff_factor=2.0)
        """
        self.name = name
        self.description = description if description else "No description provided."
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.state = ToolState.INIT

    def validate(self) -> bool:
        """
        Validate the tool's configuration.

        :return: Boolean indicating if the tool setup is valid.

        Example:
            is_valid = tool.validate()
        """
        log.info(f"Validating tool: {self.name}")
        # Default implementation always returns True
        return True

    def run(self, *args, **kwargs) -> any:
        """
        Execute the tool, calling pre and post hooks, with retry mechanism for failure handling.

        :param args: Positional arguments to be passed to the tool's logic.
        :param kwargs: Keyword arguments to be passed to the tool's logic.
        :return: The result of the tool's execution, if successful.

        Example:
            result = tool.run(param1, param2=value)
        """
        attempt = 0
        self.state = ToolState.RUNNING
        log.info(f"Tool state updated to: {self.state.value}")

        while attempt <= self.max_retries:
            try:
                log.info(f"Running tool: {self.name}, Attempt: {attempt + 1}")
                self.pre_run_hook()
                result = self._run_logic(*args, **kwargs)
                self.post_run_hook()
                self.state = ToolState.SUCCESS
                log.info(f"Tool state updated to: {self.state.value}")
                return result  # Return the result if successful
            except Exception as e:
                attempt += 1
                self._log_error(e, attempt)
                if attempt > self.max_retries:
                    self.state = ToolState.FAILED
                    log.error(f"Max retries reached for tool: {self.name}. Tool state updated to: {self.state.value}. Aborting.")
                    return None  # Return None if all retries fail
                self._retry_wait(attempt)

    def pre_run_hook(self) -> None:
        """
        Hook method to perform operations before running the tool.

        This method can be overridden by subclasses to add custom pre-execution behavior.

        Example:
            tool.pre_run_hook()
        """
        log.info(f"Running pre-run hook for tool: {self.name}")

    def post_run_hook(self) -> None:
        """
        Hook method to perform operations after running the tool.

        This method can be overridden by subclasses to add custom post-execution behavior.

        Example:
            tool.post_run_hook()
        """
        log.info(f"Running post-run hook for tool: {self.name}")

    def _run_logic(self, *args, **kwargs) -> any:
        """
        Placeholder for the main logic of the tool.

        This should be implemented by subclasses.

        :param args: Positional arguments for the tool's logic.
        :param kwargs: Keyword arguments for the tool's logic.
        :return: The result of the tool's execution.

        Example:
            result = tool._run_logic(param1, param2=value)
        """
        raise NotImplementedError("_run_logic method must be implemented by subclasses.")

    def setup_hook(self) -> None:
        """
        Hook method to perform operations during the tool's initialization.

        This method can be overridden by subclasses to perform custom setup tasks.

        Example:
            tool.setup_hook()
        """
        log.info(f"Running setup hook for tool: {self.name}")

    def _log_error(self, error: Exception, attempt: int) -> None:
        """
        Log error details for a failed run attempt.

        :param error: Exception instance representing the error.
        :param attempt: Current attempt number.

        Example:
            self._log_error(e, attempt)
        """
        log.error(f"Error while running tool {self.name}, Attempt {attempt}: {error}")

    def _retry_wait(self, attempt: int) -> None:
        """
        Wait for a duration based on the current retry attempt, using exponential backoff.

        :param attempt: Current attempt number.

        Example:
            self._retry_wait(attempt)
        """
        wait_time = self.backoff_factor ** attempt
        log.info(f"Retrying in {wait_time} seconds...")
        time.sleep(wait_time)