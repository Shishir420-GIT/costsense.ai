"""Orchestrator Agent - Coordinates all specialist agents"""

from typing import Dict, Any, Optional, List
import logging
import asyncio

from .cost_analyst import cost_analyst
from .infrastructure_analyst import infrastructure_analyst
from .financial_analyst import financial_analyst
from .remediation_specialist import remediation_specialist
from src.mock.azure_data_generator import azure_data_generator

logger = logging.getLogger(__name__)


class AzureCostOrchestrator:
    """
    Master orchestrator for Azure cost optimization

    Coordinates specialist agents to provide comprehensive cost optimization analysis.
    """

    def __init__(self):
        """Initialize the orchestrator"""
        logger.info("Azure Cost Orchestrator initialized (fallback mode)")

    def _route_query(self, query: str) -> List[str]:
        """
        Determine which agents should handle the query

        Returns list of agent names to invoke
        """
        query_lower = query.lower()
        agents = []

        # Cost-related keywords
        if any(word in query_lower for word in ['cost', 'spend', 'expense', 'price', 'bill', 'top']):
            agents.append('cost')

        # Infrastructure keywords
        if any(word in query_lower for word in ['vm', 'virtual machine', 'compute', 'storage', 'resource', 'infrastructure']):
            agents.append('infrastructure')

        # Financial keywords
        if any(word in query_lower for word in ['roi', 'return', 'investment', 'payback', 'financial', 'savings']):
            agents.append('financial')

        # Remediation keywords
        if any(word in query_lower for word in ['fix', 'implement', 'action', 'remediat', 'how to', 'steps', 'plan']):
            agents.append('remediation')

        # If no specific routing, use cost analyst as default
        if not agents:
            agents.append('cost')

        return agents

    async def analyze(self, query: str) -> str:
        """
        Main analysis entry point

        Args:
            query: User's cost optimization question

        Returns:
            Comprehensive analysis with recommendations
        """
        try:
            # Route query to appropriate agents
            agent_names = self._route_query(query)

            results = []

            # Call each relevant agent
            for agent_name in agent_names:
                if agent_name == 'cost':
                    result = await cost_analyst.analyze(query)
                    results.append(f"**Cost Analysis:**\n{result}")
                elif agent_name == 'infrastructure':
                    result = await infrastructure_analyst.analyze(query)
                    results.append(f"**Infrastructure Analysis:**\n{result}")
                elif agent_name == 'financial':
                    result = await financial_analyst.analyze(query)
                    results.append(f"**Financial Analysis:**\n{result}")
                elif agent_name == 'remediation':
                    result = await remediation_specialist.create_plan(query)
                    results.append(f"**Action Plan:**\n{result}")

            # Combine results
            combined = "\n\n".join(results)
            return combined

        except Exception as e:
            logger.error(f"Orchestrator analysis failed: {e}")
            return f"Error during analysis: {str(e)}"

    async def parallel_analysis(self, query: str) -> Dict[str, str]:
        """
        Run all agents in parallel for comprehensive analysis

        Args:
            query: User's cost optimization question

        Returns:
            Dictionary with results from each specialist agent
        """
        try:
            # Run all agents concurrently
            cost_task = cost_analyst.analyze(query)
            infra_task = infrastructure_analyst.analyze(query)
            financial_task = financial_analyst.analyze(query)
            remediation_task = remediation_specialist.create_plan(query)

            cost_result, infra_result, financial_result, remediation_result = await asyncio.gather(
                cost_task,
                infra_task,
                financial_task,
                remediation_task,
                return_exceptions=True
            )

            return {
                "cost_analysis": str(cost_result) if not isinstance(cost_result, Exception) else f"Error: {cost_result}",
                "infrastructure_analysis": str(infra_result) if not isinstance(infra_result, Exception) else f"Error: {infra_result}",
                "financial_analysis": str(financial_result) if not isinstance(financial_result, Exception) else f"Error: {financial_result}",
                "remediation_plan": str(remediation_result) if not isinstance(remediation_result, Exception) else f"Error: {remediation_result}"
            }

        except Exception as e:
            logger.error(f"Parallel analysis failed: {e}")
            return {
                "error": f"Parallel analysis failed: {str(e)}"
            }

    async def comprehensive_analysis(self, query: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis with all data and agents

        Args:
            query: User's cost optimization question

        Returns:
            Complete analysis with dashboard data and agent insights
        """
        try:
            # Get comprehensive data
            dashboard_data = azure_data_generator.generate_comprehensive_analysis()

            # Run parallel agent analysis
            agent_results = await self.parallel_analysis(query)

            return {
                "query": query,
                "dashboard_data": dashboard_data,
                "agent_analysis": agent_results,
                "timestamp": dashboard_data.get("timestamp")
            }

        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return {
                "error": f"Comprehensive analysis failed: {str(e)}"
            }


# Singleton instance
azure_orchestrator = AzureCostOrchestrator()
