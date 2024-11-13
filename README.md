# Fluxr

A modular hyperautomation framework inspired by CrewAI.

## Features

- Modular architecture with standardized interfaces
- Comprehensive logging and real-time execution feedback
- AI agent integration
- Event-driven automation
- External service connectors (Excel, Telegram, etc.)
- Task-based workflow orchestration

## Installation

```bash
pip install fluxr
```

## Quick Start

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

## Documentation

For detailed documentation, visit [docs.fluxr.io](https://docs.fluxr.io)

## License

This project is licensed under the MIT License - see the LICENSE file for details.