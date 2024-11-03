# src/core/listener_base.py
import logging
from core.listener.listener_protocol import AutomationListenerProtocol

log = logging.getLogger("core")

class ListenerBase(AutomationListenerProtocol):
    """
    Base class for defining Automation Listeners.
    """
    def __init__(self, workflow):
        self.workflow = workflow

    def start(self):
        raise NotImplementedError("The 'start' method must be implemented by subclasses.")

    def stop(self):
        raise NotImplementedError("The 'stop' method must be implemented by subclasses.")

    def on_event(self):
        """
        Handles the event when triggered, running the workflow.
        """
        try:
            log.info("Event triggered, starting workflow execution.")
            self.workflow.run()
        except Exception as e:
            log.error(f"Failed to execute workflow: {str(e)}")
