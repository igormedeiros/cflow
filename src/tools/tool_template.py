# File: src/cflow/tool_template.py
from cflow.tool_base import ToolBase
from cflow.logger import log

class ExampleTool(ToolBase):
    def __init__(self, name: str = "ExampleTool", description: str = None, max_retries: int = 3, backoff_factor: float = 2.0):
        """
        Initialize the ExampleTool with default settings.

        :param name: Name of the tool.
        :param description: Optional description of the tool.
        :param max_retries: Maximum number of retries in case of failure.
        :param backoff_factor: Factor by which the wait time increases with each retry.
        """
        super().__init__(name, description if description else "This is an example implementation of a tool.", max_retries, backoff_factor)
        self.result = None  # Placeholder for result

    def _run_logic(self, *args, **kwargs) -> str:
        """
        Main logic for the ExampleTool. This is where the specific tool's task is executed.

        :param args: Positional arguments for the tool's logic.
        :param kwargs: Keyword arguments for the tool's logic.
        :return: A string indicating the result of the tool.
        """
        log.info(f"Executing main logic of {self.name}.")
        # Example logic: simply combine all args and kwargs into a message.
        message = f"Args: {args}, Kwargs: {kwargs}"
        log.info(f"Logic executed successfully for {self.name}: {message}")
        self.result = message
        return message

    def validate(self) -> bool:
        """
        Validate the tool's configuration.

        :return: Boolean indicating if the tool setup is valid.
        """
        log.info(f"Validating tool: {self.name}")
        # Perform validation checks here. For now, we assume it is always valid.
        return True

    def pre_run_hook(self) -> None:
        """
        Example of a pre-run hook that runs before the main logic.
        """
        log.info(f"Custom pre-run logic for {self.name}")

    def post_run_hook(self) -> None:
        """
        Example of a post-run hook that runs after the main logic.
        """
        log.info(f"Custom post-run logic for {self.name}")

# Usage Example
# --------------------------------------------------------
# This is an example of how to use the tool template to create a new tool.
#
# tool = ExampleTool(name="MyCustomTool", description="Custom example tool")
# if tool.validate():
#     result = tool.run("param1", param2="value")
#     log.info(f"Result from tool: {result}")
# --------------------------------------------------------

# Documentation on Hooks, Validation, and Execution
# --------------------------------------------------------
# The `ExampleTool` class inherits from `ToolBase` and provides a concrete implementation.
# The `_run_logic()` method is where the main task of the tool is performed. This must be overridden by each new tool.
# Hooks (`pre_run_hook` and `post_run_hook`) are included to allow developers to add custom logic before and after
# the main task is executed. These hooks provide extensibility without needing to modify the core logic of `ToolBase`.
#
# Validation (`validate()`) can be customized to ensure that the tool is properly configured before running.
# This ensures that any required attributes or conditions are checked beforehand.
# --------------------------------------------------------
