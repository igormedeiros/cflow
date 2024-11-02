# File: src/cflow/task_protocol.py
from abc import ABC, abstractmethod

class TaskProtocol(ABC):
    @abstractmethod
    def execute(self) -> None:
        """
        Execute the task's main logic.

        Example:
            task = MyCustomTask()
            task.execute()
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the task before execution.

        :return: Boolean indicating if the task is valid.

        Example:
            task = MyCustomTask()
            is_valid = task.validate()
        """
        pass

    @abstractmethod
    def pre_execute_hook(self) -> None:
        """
        Hook method to perform operations before task execution.

        Example:
            task = MyCustomTask()
            task.pre_execute_hook()
        """
        pass

    @abstractmethod
    def post_execute_hook(self) -> None:
        """
        Hook method to perform operations after task execution.

        Example:
            task = MyCustomTask()
            task.post_execute_hook()
        """
        pass