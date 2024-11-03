# File: src/cflow/workflow.py
from typing import List, Optional
import time
from enum import Enum
from cflow.logger import log
from cflow.connector_base import ConnectorBase, NotifiableConnector
from cflow.task_base import TaskBase
from cflow.tool_base import ToolBase
from cflow.automation_listener_base import AutomationListener


class WorkflowState(Enum):
    READY = "Ready"
    RUNNING = "Running"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    FAILED = "Failed"


class Workflow:
    def __init__(self,
                 name: str,
                 description: Optional[str] = None,
                 tools: Optional[List[ToolBase]] = None,
                 connectors: Optional[List[ConnectorBase]] = None,
                 tasks: Optional[List[TaskBase]] = None,
                 listeners: Optional[List[AutomationListener]] = None):
        """
        Initializes a Workflow instance with the given name, description, tools, connectors, tasks, and listeners.

        :param name: Name of the workflow.
        :param description: Optional description of the workflow.
        :param tools: List of tools to be used in the workflow.
        :param connectors: List of connectors to be used in the workflow.
        :param tasks: List of tasks to be executed as part of the workflow.
        :param listeners: List of listeners that trigger the workflow automatically.
        """
        self.name = name
        self.description = description if description else "No description provided."
        self.tasks: List[TaskBase] = tasks if tasks else []
        self.connectors: List[ConnectorBase] = connectors if connectors else []
        self.tools: List[ToolBase] = tools if tools else []
        self.listeners: List[AutomationListener] = listeners if listeners else []
        self.state = WorkflowState.READY
        self.metrics = {
            "total_execution_time": 0,
            "failed_tasks": 0,
            "successful_tasks": 0,
        }

    def add_task(self, task: TaskBase):
        """
        Adds a task to the workflow.

        :param task: The task to be added.
        """
        self.tasks.append(task)
        log.info(f"Task added: {task.name}")

    def add_connector(self, connector: ConnectorBase):
        """
        Adds a connector to the workflow.

        :param connector: The connector to be added.
        """
        self.connectors.append(connector)
        log.info(f"Connector added: {connector.name}")

    def add_tool(self, tool: ToolBase):
        """
        Adds a tool to the workflow.

        :param tool: The tool to be added.
        """
        self.tools.append(tool)
        log.info(f"Tool added: {tool.name}")

    def add_listener(self, listener: AutomationListener):
        """
        Adds a listener to the workflow.

        :param listener: The listener to be added.
        """
        self.listeners.append(listener)
        log.info(f"Listener added: {listener.__class__.__name__}")

    def _connect_connectors(self):
        """
        Connect all connectors after validating their configuration.
        """
        for connector in self.connectors:
            if not connector.validate_connection():
                log.error(f"Connector '{connector.name}' validation failed. Skipping connection.")
                continue
        for connector in self.connectors:
            attempt = 0
            while attempt < 3:  # Retry mechanism
                try:
                    log.info(f"Attempting to connect: {connector.name}, Attempt: {attempt + 1}")
                    connector.connect()
                    break
                except Exception as e:
                    log.error(f"Connection attempt {attempt + 1} failed for {connector.name}: {e}")
                    attempt += 1
                    time.sleep(2 ** attempt)  # Exponential backoff
            else:
                log.error(f"Failed to connect to connector: {connector.name} after 3 attempts")
                raise Exception(f"Connector '{connector.name}' could not be connected after multiple attempts.")

    def _notify_connectors(self):
        for connector in self.connectors:
            if isinstance(connector, NotifiableConnector):
                connector.notify()

    def listen(self):
        """
        Starts all listeners to wait for trigger events.
        """
        if not self.listeners:
            log.info(f"No listeners found for workflow '{self.name}'. Defaulting to manual execution.")
            self.run()
        else:
            log.info(f"Starting listeners for workflow '{self.name}'...")
            for listener in self.listeners:
                listener.start()
                log.info(f"Listener '{listener.name}' started for workflow '{self.name}'.")

    def run(self, callback=None, tool_params: Optional[dict] = None):
        """
        Runs the workflow by connecting to all connectors, executing all tasks, and utilizing all tools.
        Enhanced error handling to differentiate between different error scenarios.
        """
        self.state = WorkflowState.RUNNING
        log.info(f"Workflow '{self.name}' state updated to: {self.state.value}")
        start_time = time.time()

        try:
            # Connect all connectors with validation
            try:
                self._connect_connectors()
            except Exception as ce:
                self.state = WorkflowState.FAILED
                log.error(f"Connection error in workflow '{self.name}': {ce}")
                return

            # Execute all tasks
            for task in self.tasks:
                try:
                    log.info(f"Starting execution of task: {task.name}")
                    start_task_time = time.time()
                    if task.validate():
                        task.execute()
                        self.metrics["successful_tasks"] += 1
                        log.info(f"Task '{task.name}' executed successfully.")
                    else:
                        log.warning(f"Task '{task.name}' validation failed. Skipping execution.")
                    end_task_time = time.time()
                    log.info(f"Task '{task.name}' completed in {end_task_time - start_task_time} seconds.")
                except Exception as e:
                    self.metrics["failed_tasks"] += 1
                    log.error(f"Error while executing task '{task.name}': {e}")

            # Execute all tools
            for tool in self.tools:
                try:
                    log.info(f"Starting execution of tool: {tool.name}")
                    start_tool_time = time.time()
                    if tool.validate():
                        params = tool_params.get(tool.name, {}) if tool_params else {}
                        result = tool.run(**params)
                        log.info(f"Tool '{tool.name}' executed with result: {result}")
                    else:
                        log.warning(f"Tool '{tool.name}' validation failed. Skipping execution.")
                    end_tool_time = time.time()
                    log.info(f"Tool '{tool.name}' completed in {end_tool_time - start_tool_time} seconds.")
                except Exception as e:
                    log.error(f"Error while executing tool '{tool.name}': {e}")

            # Notify using connectors if applicable
            self._notify_connectors()

            # Update state and metrics
            self.state = WorkflowState.COMPLETED
            end_time = time.time()
            self.metrics["total_execution_time"] = end_time - start_time
            log.info(f"Workflow '{self.name}' completed in {self.metrics['total_execution_time']} seconds.")

            # Callback if provided
            if callback:
                callback(self)

        except Exception as e:
            log.error(f"Unknown error in workflow '{self.name}': {e}")
            self.state = WorkflowState.FAILED
            log.error(f"Workflow '{self.name}' state updated to: {self.state.value} due to error: {e}")

    def stop_listeners(self):
        for listener in self.listeners:
            listener.stop()
            log.info(f"Listener for workflow '{self.name}' stopped.")

    def get_metrics(self):
        """
        Get the metrics of the workflow execution.

        :return: A dictionary containing metrics such as total execution time, failed tasks, and successful tasks.
        """
        return self.metrics

# Usage Example
# --------------------------------------------------------
# This is an example of how to use the Workflow class to create a new workflow.
#
# from connectors.telegram_connector import TelegramConnector
# from tasks.excel_to_telegram_task import ExcelToTelegramTask
# from tools.example_tool import ExampleTool
#
# workflow = Workflow(name="SampleWorkflow", description="A workflow that demonstrates connectors, tasks, and tools")
#
# telegram_connector = TelegramConnector(name="Telegram Connector", token="YOUR_TOKEN", chat
