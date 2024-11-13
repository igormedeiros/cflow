# Welcome to Fluxr

Fluxr is a powerful hyperautomation framework designed for building modular, scalable automation workflows. It provides a robust foundation for integrating AI agents, external services, and custom tools into your automation pipelines.

## Key Features

- **Modular Architecture**: Build workflows using reusable components
- **AI Integration**: Seamlessly incorporate AI agents into your automation
- **External Connectors**: Connect to various services and data sources
- **Real-time Feedback**: Get detailed execution insights and logging
- **Event-driven**: Trigger workflows based on events
- **Type Safety**: Built with Python type hints for better development experience

## Example Usage

```python
from fluxr import Flux, Task, ExcelConnector, AgentTool, TelegramConnector

# Configure task
task = Task(
    name="ExcelSummaryTask",
    connectors=[ExcelConnector(), TelegramConnector()],
    tools=[AgentTool(model="gpt-3.5-turbo", purpose="summarization")]
)

# Create and run workflow
flux = Flux(verbose=True, log=True)
flux.add_task(task)
flux.run()
```

## Getting Started

Check out our [Quick Start](getting-started/quickstart.md) guide to begin building your first Fluxr workflow.