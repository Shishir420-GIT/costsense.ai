import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import Agent, AgentResult
from .cost_analysis_agent import CostAnalysisAgent
from .optimization_agent import OptimizationAgent
from .explanation_agent import ExplanationAgent
from ..ai.ollama_client import OllamaClient, get_ollama_client
from ..logging_config import get_logger

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple agents for complex tasks"""

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.ollama_client = ollama_client
        self.agents: Dict[str, Agent] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize all agents"""
        if self._initialized:
            return

        if not self.ollama_client:
            self.ollama_client = await get_ollama_client()

        # Create agent instances
        self.agents = {
            "cost_analysis": CostAnalysisAgent(self.ollama_client),
            "optimization": OptimizationAgent(self.ollama_client),
            "explanation": ExplanationAgent(self.ollama_client),
        }

        self._initialized = True
        logger.info("Agent orchestrator initialized", agent_count=len(self.agents))

    async def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> AgentResult:
        """Execute a single agent"""
        await self.initialize()

        agent = self.agents.get(agent_name)
        if not agent:
            return AgentResult(
                agent_name=agent_name,
                success=False,
                error=f"Agent not found: {agent_name}",
                execution_time_ms=0,
            )

        logger.info(f"Executing agent: {agent_name}")
        result = await agent.execute(context)
        logger.info(
            f"Agent completed: {agent_name}",
            success=result.success,
            execution_time_ms=result.execution_time_ms,
        )

        return result

    async def execute_parallel(
        self, agent_tasks: List[tuple[str, Dict[str, Any]]]
    ) -> Dict[str, AgentResult]:
        """Execute multiple agents in parallel"""
        await self.initialize()

        logger.info(f"Executing {len(agent_tasks)} agents in parallel")

        # Create tasks
        tasks = []
        agent_names = []
        for agent_name, context in agent_tasks:
            tasks.append(self.execute_agent(agent_name, context))
            agent_names.append(agent_name)

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build result dictionary
        result_dict = {}
        for agent_name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                result_dict[agent_name] = AgentResult(
                    agent_name=agent_name,
                    success=False,
                    error=str(result),
                    execution_time_ms=0,
                )
            else:
                result_dict[agent_name] = result

        logger.info("Parallel execution completed", agent_count=len(result_dict))
        return result_dict

    async def full_analysis(
        self, cost_data: List[Dict[str, Any]], time_period: str = "30 days"
    ) -> Dict[str, Any]:
        """
        Run full cost analysis pipeline:
        1. Cost Analysis Agent
        2. Optimization Agent (using analysis results)
        3. Summary aggregation
        """
        await self.initialize()

        logger.info("Starting full analysis pipeline")
        start_time = datetime.utcnow()

        # Step 1: Cost Analysis
        analysis_result = await self.execute_agent(
            "cost_analysis",
            {
                "cost_data": cost_data,
                "time_period": time_period,
                "provider": "all",
            },
        )

        if not analysis_result.success:
            logger.error("Cost analysis failed", error=analysis_result.error)
            return {
                "success": False,
                "error": analysis_result.error,
                "timestamp": start_time,
            }

        # Step 2: Optimization Analysis
        optimization_result = await self.execute_agent(
            "optimization",
            {
                "cost_data": cost_data,
                "analysis_result": analysis_result.result,
                "threshold": 100.0,
            },
        )

        # Aggregate results
        pipeline_result = {
            "success": True,
            "timestamp": start_time,
            "execution_time_ms": (
                analysis_result.execution_time_ms
                + optimization_result.execution_time_ms
            ),
            "analysis": analysis_result.result if analysis_result.success else None,
            "optimization": (
                optimization_result.result if optimization_result.success else None
            ),
            "summary": self._create_summary(analysis_result, optimization_result),
        }

        logger.info(
            "Full analysis pipeline completed",
            execution_time_ms=pipeline_result["execution_time_ms"],
        )

        return pipeline_result

    def _create_summary(
        self, analysis_result: AgentResult, optimization_result: AgentResult
    ) -> Dict[str, Any]:
        """Create executive summary from agent results"""
        summary = {
            "status": "completed",
            "agents_executed": 2,
            "agents_successful": sum(
                [analysis_result.success, optimization_result.success]
            ),
        }

        if analysis_result.success and analysis_result.result:
            summary["total_cost"] = analysis_result.result.get("total_cost", 0)
            summary["resource_count"] = analysis_result.result.get("resource_count", 0)
            summary["top_insight"] = (
                analysis_result.result.get("summary", "")[:200] + "..."
            )

        if optimization_result.success and optimization_result.result:
            summary["optimization_opportunities"] = len(
                optimization_result.result.get("opportunities", [])
            )
            summary["potential_savings"] = optimization_result.result.get(
                "total_potential_savings", 0
            )

        return summary


# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


async def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
        await _orchestrator.initialize()
    return _orchestrator
