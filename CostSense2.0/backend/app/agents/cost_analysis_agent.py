from typing import Dict, Any
from datetime import datetime
import time
from .base import Agent, AgentResult
from ..ai.prompts import SystemPrompts


class CostAnalysisAgent(Agent):
    """Agent for analyzing cost data and identifying patterns"""

    def __init__(self, ollama_client):
        super().__init__(ollama_client, "CostAnalysisAgent")

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Analyze cost data and provide insights

        Expected context:
        - cost_data: List of cost records
        - time_period: Period being analyzed
        - provider: Optional cloud provider filter
        """
        start_time = time.time()

        try:
            cost_data = context.get("cost_data", [])
            time_period = context.get("time_period", "30 days")
            provider = context.get("provider", "all providers")

            if not cost_data:
                return self._create_result(
                    success=False,
                    error="No cost data provided",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

            # Prepare cost summary
            total_cost = sum(item.get("cost", 0) for item in cost_data)
            resource_types = {}
            regions = {}

            for item in cost_data:
                rt = item.get("resource_type", "unknown")
                region = item.get("region", "unknown")
                cost = item.get("cost", 0)

                resource_types[rt] = resource_types.get(rt, 0) + cost
                regions[region] = regions.get(region, 0) + cost

            # Sort by cost
            top_resources = sorted(
                resource_types.items(), key=lambda x: x[1], reverse=True
            )[:5]
            top_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:5]

            # Build prompt for LLM
            prompt = f"""Analyze the following cost data for {provider} over {time_period}:

Total Cost: ${total_cost:,.2f}
Number of Resources: {len(cost_data)}

Top 5 Resource Types by Cost:
{chr(10).join(f"- {rt}: ${cost:,.2f} ({cost/total_cost*100:.1f}%)" for rt, cost in top_resources)}

Top 5 Regions by Cost:
{chr(10).join(f"- {region}: ${cost:,.2f} ({cost/total_cost*100:.1f}%)" for region, cost in top_regions)}

Provide a detailed analysis including:
1. Summary of spending patterns
2. Top cost drivers
3. Any anomalies or unusual patterns
4. Spending trends
5. Recommendations for further investigation

Response format:
{{"summary": "...", "top_drivers": [...], "anomalies": [...], "trends": {{}}, "recommendations": [...]}}
"""

            # Get AI analysis
            analysis = await self._generate_with_retry(
                prompt=prompt,
                system_prompt=SystemPrompts.COST_ANALYSIS,
                temperature=0.3,
            )

            # Enhance with calculated data
            analysis["total_cost"] = total_cost
            analysis["resource_count"] = len(cost_data)
            analysis["time_period"] = time_period
            analysis["provider"] = provider

            execution_time = int((time.time() - start_time) * 1000)

            self.logger.info(
                "Cost analysis completed",
                total_cost=total_cost,
                resource_count=len(cost_data),
                execution_time_ms=execution_time,
            )

            return self._create_result(
                success=True,
                result=analysis,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error("Cost analysis failed", error=str(e))

            return self._create_result(
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
            )
