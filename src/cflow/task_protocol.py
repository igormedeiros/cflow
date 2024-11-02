# File: src/cflow/task_protocol.py
from abc import ABC, abstractmethod

class TaskProtocol(ABC):
    @abstractmethod
    def execute(self) -> None:
        """
        Execute the task's main logic.
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the task before execution.
        :return: Boolean indicating if the task is valid.
        """
        pass

    @abstractmethod
    def pre_execute_hook(self) -> None:
        """
        Hook method to perform operations before task execution.
        """
        pass

    @abstractmethod
    def post_execute_hook(self) -> None:
        """
        Hook method to perform operations after task execution.
        """
        pass