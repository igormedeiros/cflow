import asyncio
from typing import List, Literal
import logging
from loguru import logger
from colorama import init, Fore
from .base import Task

TriggerMode = Literal["manual", "auto"]

class Flux:
    def __init__(
        self,
        verbose: bool = False,
        log: bool = True,
        trigger_mode: TriggerMode = "manual"
    ):
        self.verbose = verbose
        self.log = log
        self.trigger_mode = trigger_mode
        self.tasks: List[Task] = []
        
        # Initialize colorama for cross-platform colored output
        init()
        
        # Configure logging
        if log:
            logger.add(
                "fluxr.log",
                rotation="1 day",
                retention="7 days",
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
            )
    
    def add_task(self, task: Task) -> None:
        """Add a task to the workflow."""
        self.tasks.append(task)
        if self.verbose:
            print(f"{Fore.GREEN}Added task: {task.name}{Fore.RESET}")
        if self.log:
            logger.debug(f"Task added: {task.name}")
    
    async def _execute_tasks(self) -> None:
        """Execute all tasks in sequence."""
        for task in self.tasks:
            if self.verbose:
                print(f"{Fore.YELLOW}Executing task: {task.name}{Fore.RESET}")
            if self.log:
                logger.info(f"Starting task execution: {task.name}")
                
            try:
                # Activate triggers if in auto mode
                if self.trigger_mode == "auto":
                    for trigger in task.triggers:
                        if self.verbose:
                            print(f"{Fore.CYAN}Activating trigger: {trigger.name}{Fore.RESET}")
                        await trigger.activate()
                
                result = await task.execute()
                
                # Deactivate triggers if in auto mode
                if self.trigger_mode == "auto":
                    for trigger in task.triggers:
                        await trigger.deactivate()
                
                if self.verbose:
                    print(f"{Fore.GREEN}Task completed: {task.name}{Fore.RESET}")
                if self.log:
                    logger.success(f"Task completed: {task.name}")
            except Exception as e:
                if self.verbose:
                    print(f"{Fore.RED}Task failed: {task.name} - {str(e)}{Fore.RESET}")
                if self.log:
                    logger.error(f"Task failed: {task.name} - {str(e)}")
                raise
    
    def run(self) -> None:
        """Run the workflow."""
        if self.verbose:
            print(f"{Fore.CYAN}Starting Fluxr workflow in {self.trigger_mode} mode{Fore.RESET}")
        if self.log:
            logger.info(f"Starting Fluxr workflow in {self.trigger_mode} mode")
            
        try:
            asyncio.run(self._execute_tasks())
            if self.verbose:
                print(f"{Fore.CYAN}Workflow completed successfully{Fore.RESET}")
            if self.log:
                logger.success("Workflow completed successfully")
        except Exception as e:
            if self.verbose:
                print(f"{Fore.RED}Workflow failed: {str(e)}{Fore.RESET}")
            if self.log:
                logger.error(f"Workflow failed: {str(e)}")
            raise