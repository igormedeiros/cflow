import asyncio
from datetime import datetime
from fluxr import Flux, Task, Trigger

class TimeBasedTrigger(Trigger):
    def __init__(self, execution_time: datetime):
        super().__init__(
            name="TimeBasedTrigger",
            event_type="time",
            description="Trigger task at specific time"
        )
        self.execution_time = execution_time
        self._active = False
        
    async def activate(self) -> None:
        """Activate the time-based trigger."""
        self._active = True
        while self._active:
            now = datetime.now()
            if now >= self.execution_time:
                print(f"Trigger activated at {now}")
                break
            await asyncio.sleep(1)
            
    async def deactivate(self) -> None:
        """Deactivate the trigger."""
        self._active = False

# Create task with custom trigger
execution_time = datetime.now().replace(hour=15, minute=0, second=0)  # 3 PM
trigger = TimeBasedTrigger(execution_time)

task = Task(
    name="TimedTask",
    triggers=[trigger]
)

# Run workflow
flux = Flux(verbose=True)
flux.add_task(task)
flux.run()