from typing import Dict, Any
import time
from .base import Agent, AgentResult
from ..ai.prompts import SystemPrompts


class OptimizationAgent(Agent):
    """Agent for identifying cost optimization opportunities"""

    def __init__(self, ollama_client):
        super().__init__(ollama_client, "OptimizationAgent")

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Identify cost optimization opportunities

        Expected context:
        - cost_data: List of cost records
        - analysis_result: Optional result from CostAnalysisAgent
        - threshold: Minimum cost to consider (default: $100)
        """
        start_time = time.time()

        try:
            cost_data = context.get("cost_data", [])
            analysis_result = context.get("analysis_result")
            threshold = context.get("threshold", 100.0)

            if not cost_data:
                return self._create_result(
                    success=False,
                    error="No cost data provided",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

            # Filter high-cost resources
            high_cost_resources = [
                item for item in cost_data if item.get("cost", 0) >= threshold
            ]

            # Prepare optimization analysis
            total_cost = sum(item.get("cost", 0) for item in cost_data)
            high_cost_total = sum(item.get("cost", 0) for item in high_cost_resources)

            prompt = f"""Analyze the following high-cost resources and identify optimization opportunities:

Total Infrastructure Cost: ${total_cost:,.2f}
High-Cost Resources (>${threshold}): {len(high_cost_resources)} resources totaling ${high_cost_total:,.2f}

Sample High-Cost Resources:
"""
            # Add up to 10 sample resources
            for item in high_cost_resources[:10]:
                prompt += f"\n- {item.get('resource_type', 'Unknown')}: ${item.get('cost', 0):,.2f} in {item.get('region', 'unknown')}"

            if analysis_result:
                prompt += f"\n\nPrevious Analysis Summary:\n{analysis_result.get('summary', 'N/A')}"

            prompt += """

Identify specific cost optimization opportunities. For each opportunity:
1. Title and description
2. Estimated savings (be conservative)
3. Implementation complexity (low/medium/high)
4. Risk level (low/medium/high)
5. Step-by-step actions

Response format:
{"opportunities": [...], "total_potential_savings": 0.0, "implementation_priority": [...]}
"""

            # Get AI recommendations
            optimization = await self._generate_with_retry(
                prompt=prompt,
                system_prompt=SystemPrompts.OPTIMIZATION,
                temperature=0.4,
            )

            # Add metadata
            optimization["analyzed_resources"] = len(high_cost_resources)
            optimization["threshold"] = threshold
            optimization["total_cost"] = total_cost

            execution_time = int((time.time() - start_time) * 1000)

            self.logger.info(
                "Optimization analysis completed",
                opportunities=len(optimization.get("opportunities", [])),
                potential_savings=optimization.get("total_potential_savings", 0),
                execution_time_ms=execution_time,
            )

            return self._create_result(
                success=True,
                result=optimization,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error("Optimization analysis failed", error=str(e))

            return self._create_result(
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
            )
