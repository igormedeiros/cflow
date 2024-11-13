from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

class FluxrComponent(BaseModel, ABC):
    name: str
    description: str = ""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component."""
        pass
        
    async def pre_execute(self) -> None:
        """Hook executed before the main execution."""
        pass
        
    async def post_execute(self) -> None:
        """Hook executed after the main execution."""
        pass

class Connector(FluxrComponent):
    connection_params: Dict[str, Any] = {}
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to external service."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to external service."""
        pass
        
    async def pre_connect(self) -> None:
        """Hook executed before connection."""
        pass
        
    async def post_connect(self) -> None:
        """Hook executed after connection."""
        pass
        
    async def pre_disconnect(self) -> None:
        """Hook executed before disconnection."""
        pass
        
    async def post_disconnect(self) -> None:
        """Hook executed after disconnection."""
        pass

class Tool(FluxrComponent):
    config: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, input_data: Any) -> Any:
        """Execute the tool's main functionality."""
        pass
        
    async def pre_execute(self) -> None:
        """Hook executed before tool execution."""
        pass
        
    async def post_execute(self) -> None:
        """Hook executed after tool execution."""
        pass

class Trigger(FluxrComponent):
    event_type: str
    
    @abstractmethod
    async def activate(self) -> None:
        """Activate the trigger."""
        pass
    
    @abstractmethod
    async def deactivate(self) -> None:
        """Deactivate the trigger."""
        pass
        
    async def pre_activate(self) -> None:
        """Hook executed before trigger activation."""
        pass
        
    async def post_activate(self) -> None:
        """Hook executed after trigger activation."""
        pass
        
    async def pre_deactivate(self) -> None:
        """Hook executed before trigger deactivation."""
        pass
        
    async def post_deactivate(self) -> None:
        """Hook executed after trigger deactivation."""
        pass

class Task(FluxrComponent):
    connectors: List[Connector] = []
    tools: List[Tool] = []
    triggers: List[Trigger] = []
    
    async def pre_execute(self) -> None:
        """Hook executed before task execution."""
        pass
        
    async def post_execute(self) -> None:
        """Hook executed after task execution."""
        pass
    
    async def execute(self) -> Any:
        """Execute the task workflow."""
        # Pre-execution hook
        await self.pre_execute()
        
        try:
            # Initialize and connect components
            for connector in self.connectors:
                await connector.initialize()
                await connector.pre_connect()
                await connector.connect()
                await connector.post_connect()
                
            for tool in self.tools:
                await tool.initialize()
                
            # Execute tools with hooks
            result = None
            for tool in self.tools:
                await tool.pre_execute()
                result = await tool.execute(result)
                await tool.post_execute()
                
            # Post-execution hook
            await self.post_execute()
            
            return result
            
        finally:
            # Cleanup
            for connector in self.connectors:
                await connector.pre_disconnect()
                await connector.disconnect()
                await connector.post_disconnect()