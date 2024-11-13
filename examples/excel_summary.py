from fluxr import Flux, Task, ExcelConnector, AgentTool, TelegramConnector

# Configure connectors
excel_connector = ExcelConnector()
excel_connector.connection_params = {
    "file_path": "data/sales_report.xlsx"
}

telegram_connector = TelegramConnector()
telegram_connector.connection_params = {
    "token": "YOUR_BOT_TOKEN"
}

# Configure AI tool
summary_agent = AgentTool(
    model="gpt-3.5-turbo",
    purpose="summarization"
)
summary_agent.config = {
    "openai_api_key": "YOUR_OPENAI_API_KEY"
}

# Create task
task = Task(
    name="SalesReportSummary",
    description="Summarize sales report and send to Telegram",
    connectors=[excel_connector, telegram_connector],
    tools=[summary_agent]
)

# Create and run workflow
flux = Flux(verbose=True, log=True)
flux.add_task(task)
flux.run()