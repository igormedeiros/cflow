# Fluxr - Hyper Automation Framework

Fluxr is a Python framework for workflow automation and integration between different tools and APIs, inspired by frameworks like crewai. It allows developers to define custom data pipelines using modular triggers, connectors, tools, and tasks to orchestrate workflows.

## Project Structure

- **connectors/**: Contains connectors to connect to different data sources or APIs (e.g., Excel, REST, Telegram).
- **tools/**: Reusable tools that provide unique and independent functionality (e.g., text conversion to uppercase).
- **tasks/**: Contains tasks that combine connectors and tools to perform more complex operations.
- **flux.py**: Definition of the workflow that manages the execution of tasks and connectors.
- **main.py**: Example usage, demonstrating how to set up and run a workflow.

## Key Features

- **Modularity**: Connectors, tools, and tasks are modular components that can be combined to create complex workflows.
- **Execution Hooks**: Add custom behaviors before and after task or tool executions.
- **Resilience**: Implementation of retry mechanisms (with exponential backoff) for connectors.
- **Monitoring and Logging**: Detailed logging and monitoring of workflow metrics.
- **Workflow States**: The workflow manages its own lifecycle, with states such as Ready, Running, Paused, Completed, and Failed.

## Connectors

CFlow comes with over 60 connectors for integration with different platforms, allowing users to create versatile workflows. Here are some of the most well-known connectors:

1. **Kubernetes Connector**: Integrates with Kubernetes clusters to manage namespaces and pods.
2. **Excel Connector**: Reads data from Excel files for further processing in workflows.
3. **Telegram Connector**: Sends messages to Telegram chats for notification purposes.
4. **REST API Connector**: Generic connector for making HTTP requests to external REST APIs.
5. **Slack Connector**: Integrates with Slack to send messages to channels or users.
6. **Twilio Connector**: Enables sending SMS messages via the Twilio API.

## Requirements

- Python 3.8+
- Dependencies specified in `requirements.txt`

## Installation

Clone this repository and install the dependencies using `pip`:

```bash
$ git clone https://github.com/igormedeiros/cflow
$ cd core
$ pip install -r requirements.txt
```

## Usage

The `main.py` file is an example of how to create and execute a simple workflow that:

1. Reads data from an Excel file.
2. Sends the read data to a Telegram chat.

### Running the Example

Before running the example, make sure to fill in the correct information in `main.py`, such as the Excel file path (`file_path`) and the Telegram bot credentials (`token` and `chat_id`). Then, run the script:

```bash
$ python main.py
```

### Workflow Example

```python
from core.flux.flux import Flux
from components.connectors.excel.excel_connector import ExcelConnector
from components.connectors.telegram.telegram_connector import TelegramConnector
from components.tasks.excel_to_telegram_task import ExcelToTelegramTask


def main():
    excel_connector = ExcelConnector(name="Excel Connector", file_path="data.xlsx")
    telegram_connector = TelegramConnector(name="Telegram Notifier", token="your_telegram_bot_token",
                                           chat_id="your_chat_id")

    excel_to_telegram_task = ExcelToTelegramTask(
        name="Excel to Telegram Task",
        description="Reads data from Excel and sends it to Telegram",
        connectors=[excel_connector, telegram_connector]
    )

    workflow = Flux(
        name="Sample Workflow",
        description="This workflow reads data from an Excel file and sends it to a Telegram chat",
        connectors=[excel_connector, telegram_connector],
        tasks=[excel_to_telegram_task]
    )

    workflow.run()


if __name__ == "__main__":
    main()
```

## Workflow Structure

- **Connectors**: Used to integrate with external data sources, such as files or APIs. Examples: `ExcelConnector`, `TelegramConnector`.
- **Tasks**: Tasks are units of work that use connectors and tools to execute operations. Example: `ExcelToTelegramTask`.
- **Tools**: These are smaller, reusable functionalities that assist in the operations carried out by tasks. Example: `UpperCaseTool`.

## Developing New Components

### Creating a New Connector

1. Create a class that inherits from `ConnectorBase`.
2. Implement the `connect()` and `validate()` methods.
3. Add additional functionalities as needed.

### Creating a New Task

1. Create a class that inherits from `TaskBase`.
2. Implement the `execute()` method, using the necessary connectors and tools.
3. Validate the data and add logs to monitor the execution.

### Creating a New Tool

1. Create a class that inherits from `ToolBase`.
2. Implement the `run()` method, and if necessary, `pre_run_hook()` and `post_run_hook()`.

## Contribution

Contributions are welcome! Feel free to open issues or pull requests on the repository to add new features, fix bugs, or improve documentation.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
