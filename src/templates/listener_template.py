# listener_template.py
import logging
from core.listener.listener_base import AutomationListener

log = logging.getLogger("core")

class CustomListener(AutomationListener):
    """
    Custom listener template to be used as a base for defining specific automation listeners.
    Extend this class and implement the required methods as per the automation requirements.
    """
    def __init__(self, workflow, custom_param=None):
        """
        Initializes the CustomListener with a workflow instance.
        Optionally, additional parameters can be passed for customization.

        :param workflow: The workflow to be executed by the listener.
        :param custom_param: Optional parameter for listener customization.
        """
        super().__init__(workflow)
        self.custom_param = custom_param

    def start(self):
        """
        Starts the listener.
        Implement the logic to initialize resources or set up the necessary environment for the listener.
        """
        log.info("Starting the custom listener.")
        # Custom start logic here
        # Example: Setting up connections or preparing the listener to receive events
        pass

    def stop(self):
        """
        Stops the listener.
        Implement the logic to properly release resources or shut down the listener.
        """
        log.info("Stopping the custom listener.")
        # Custom stop logic here
        # Example: Closing connections or cleaning up any allocated resources
        pass

    def on_event(self, event):
        """
        Handles the event when triggered.
        Implement the specific logic for processing incoming events.

        :param event: The event that triggers the workflow.
        """
        try:
            log.info(f"Event received: {event}, starting workflow execution.")
            # Custom logic to handle the event can be added here before running the workflow
            self.workflow.run()
        except Exception as e:
            log.error(f"Failed to execute workflow: {str(e)}")
