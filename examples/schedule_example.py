from fluxr import Flux, Task, ScheduleTrigger, AgentTool
from datetime import timedelta

async def process_data():
    print("Processing scheduled task...")

# Create schedule trigger
trigger = ScheduleTrigger(
    name="DataProcessingTrigger",
    interval=timedelta(minutes=5),
    callback=process_data
)

# Configure task with trigger
task = Task(
    name="ScheduledProcessingTask",
    triggers=[trigger],
    tools=[AgentTool(model="gpt-3.5-turbo", purpose="data_processing")]
)

# Create and run workflow
flux = Flux(verbose=True, log=True)
flux.add_task(task)
flux.run()