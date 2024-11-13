from datetime import datetime, timedelta
from typing import Optional, Callable, Awaitable
from ..base import Trigger

class ScheduleTrigger(Trigger):
    def __init__(
        self,
        name: str = "ScheduleTrigger",
        interval: timedelta = timedelta(minutes=5),
        callback: Optional[Callable[[], Awaitable[None]]] = None
    ):
        super().__init__(name=name, event_type="schedule")
        self.interval = interval
        self.callback = callback
        self._active = False
        
    async def activate(self) -> None:
        """Activate the schedule trigger."""
        self._active = True
        while self._active:
            if self.callback:
                await self.callback()
            await asyncio.sleep(self.interval.total_seconds())
            
    async def deactivate(self) -> None:
        """Deactivate the schedule trigger."""
        self._active = False