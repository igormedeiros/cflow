from fluxr import Flux, Task, ScheduleTrigger
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
    triggers=[trigger]
)

# Example 1: Manual mode (triggers won't activate)
flux_manual = Flux(verbose=True, trigger_mode="manual")
flux_manual.add_task(task)
flux_manual.run()

# Example 2: Auto mode (triggers will activate)
flux_auto = Flux(verbose=True, trigger_mode="auto")
flux_auto.add_task(task)
flux_auto.run()