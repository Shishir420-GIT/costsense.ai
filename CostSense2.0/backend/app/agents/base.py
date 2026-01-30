from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from ..ai.ollama_client import OllamaClient
from ..logging_config import get_logger

logger = get_logger(__name__)


class AgentResult(BaseModel):
    """Result from an agent execution"""
    agent_name: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: int
    timestamp: datetime = datetime.utcnow()


class Agent(ABC):
    """Base class for AI agents"""

    def __init__(self, ollama_client: OllamaClient, name: str):
        self.ollama_client = ollama_client
        self.name = name
        self.logger = get_logger(f"{__name__}.{name}")

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute the agent with given context"""
        pass

    async def _generate_with_retry(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """Generate JSON response with retry logic"""
        try:
            response = await self.ollama_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )
            return response
        except Exception as e:
            self.logger.error(f"Agent generation failed", error=str(e))
            raise

    def _create_result(
        self,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        execution_time_ms: int = 0,
    ) -> AgentResult:
        """Create an agent result"""
        return AgentResult(
            agent_name=self.name,
            success=success,
            result=result,
            error=error,
            execution_time_ms=execution_time_ms,
        )
