from typing import Any, Optional
import openai
from ..base import Tool

class AgentTool(Tool):
    def __init__(
        self,
        name: str = "AgentTool",
        model: str = "gpt-3.5-turbo",
        purpose: str = "general"
    ):
        super().__init__(name=name)
        self.model = model
        self.purpose = purpose
        
    async def initialize(self) -> None:
        """Initialize the AI agent."""
        api_key = self.config.get("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        openai.api_key = api_key
        
    async def execute(self, input_data: Any) -> str:
        """Execute AI agent task."""
        if not input_data:
            raise ValueError("No input data provided")
            
        # Prepare system message based on purpose
        system_message = f"You are an AI assistant specialized in {self.purpose}."
        
        response = await openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": str(input_data)}
            ]
        )
        
        return response.choices[0].message.content