# src/cflow/automation_listener_protocol.py
from abc import ABC, abstractmethod

class AutomationListenerProtocol(ABC):
    """
    Protocol for defining Automation Listeners.
    """
    @abstractmethod
    def start(self):
        """
        Start the listener to monitor for events that trigger the workflow.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop the listener.
        """
        pass

    @abstractmethod
    def on_event(self):
        """
        Handles the event when triggered, running the workflow.
        """
        pass