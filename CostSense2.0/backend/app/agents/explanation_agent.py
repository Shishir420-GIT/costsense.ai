from typing import Dict, Any
import time
from .base import Agent, AgentResult
from ..ai.prompts import SystemPrompts


class ExplanationAgent(Agent):
    """Agent for explaining cost patterns and anomalies in simple terms"""

    def __init__(self, ollama_client):
        super().__init__(ollama_client, "ExplanationAgent")

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Generate human-friendly explanations of cost data

        Expected context:
        - question: User's question or topic to explain
        - cost_data: Optional cost data for context
        - analysis_result: Optional analysis to explain
        """
        start_time = time.time()

        try:
            question = context.get("question")
            cost_data = context.get("cost_data", [])
            analysis_result = context.get("analysis_result")

            if not question:
                return self._create_result(
                    success=False,
                    error="No question provided",
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

            # Build context for explanation
            prompt = f"User Question: {question}\n\n"

            if cost_data:
                total_cost = sum(item.get("cost", 0) for item in cost_data)
                prompt += f"Total Cost: ${total_cost:,.2f}\n"
                prompt += f"Number of Resources: {len(cost_data)}\n\n"

            if analysis_result:
                prompt += f"Analysis Summary:\n{analysis_result.get('summary', 'N/A')}\n\n"

                if "anomalies" in analysis_result:
                    prompt += "Detected Anomalies:\n"
                    for anomaly in analysis_result["anomalies"][:3]:
                        prompt += f"- {anomaly.get('description', 'Unknown')}\n"
                    prompt += "\n"

            prompt += """
Please provide a clear, concise explanation that:
1. Directly answers the user's question
2. Uses simple, non-technical language
3. Provides specific examples from the data
4. Explains WHY things are happening, not just WHAT

Response format:
{"explanation": "...", "key_points": [...], "recommendations": [...]}
"""

            # Get explanation from AI
            explanation = await self._generate_with_retry(
                prompt=prompt,
                system_prompt=SystemPrompts.EXPLANATION,
                temperature=0.5,
            )

            execution_time = int((time.time() - start_time) * 1000)

            self.logger.info(
                "Explanation generated",
                question=question[:100],
                execution_time_ms=execution_time,
            )

            return self._create_result(
                success=True,
                result=explanation,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error("Explanation generation failed", error=str(e))

            return self._create_result(
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
            )
