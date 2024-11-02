# File: src/cflow/tool_protocol.py
from abc import ABC, abstractmethod

class ToolProtocol(ABC):
    @abstractmethod
    def run(self, *args, **kwargs) -> any:
        """
        Execute the tool's main logic.

        :param args: Positional arguments for the tool.
        :param kwargs: Keyword arguments for the tool.
        :return: The result of the tool's execution.

        Example:
            tool = MyCustomTool()
            result = tool.run(param1, param2=value)
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the tool's configuration before execution.

        :return: Boolean indicating if the tool is valid.

        Example:
            tool = MyCustomTool()
            is_valid = tool.validate()
        """
        pass