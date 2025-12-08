"""Cost Analyst Agent - Analyzes Azure spending patterns and trends"""

from typing import Dict, Any, Optional
import json
import logging

from src.mock.azure_data_generator import azure_data_generator
from src.config.langchain_config import get_ollama_llm
from src.config.settings import Settings
from src.config.database import SessionLocal
from src.repositories import DashboardRepository

logger = logging.getLogger(__name__)
settings = Settings()


class CostAnalystAgent:
    """
    Specialized agent for Azure cost analysis

    Responsibilities:
    - Analyze spending patterns and trends
    - Identify cost anomalies
    - Compare historical data
    - Highlight cost spikes
    - Provide cost optimization insights
    """

    def __init__(self):
        """Initialize the cost analyst agent"""
        try:
            self.llm = get_ollama_llm()
            logger.info("Cost Analyst Agent initialized (LLM: Ollama)")
        except Exception as e:
            self.llm = None
            logger.info(f"Cost Analyst Agent initialized (LLM: Fallback - {e})")

    async def analyze(self, query: str, cost_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Perform cost analysis

        Args:
            query: User's cost question
            cost_data: Optional cost data (fetched if not provided)

        Returns:
            Detailed cost analysis response
        """
        try:
            # Fetch cost data if not provided
            if cost_data is None:
                if settings.USE_DATABASE:
                    # Get data from database
                    db = SessionLocal()
                    try:
                        dashboard_repo = DashboardRepository(db)
                        dashboard_data = dashboard_repo.get_dashboard_summary()

                        cost_data = {
                            "total_monthly_cost": dashboard_data["total_monthly_cost"],
                            "monthly_change_percent": dashboard_data["monthly_change_percent"],
                            "daily_costs": dashboard_data["daily_costs"][-7:],  # Last 7 days
                            "top_services": dashboard_data["top_services"],
                            "cost_trend": "increasing" if dashboard_data["monthly_change_percent"] > 0 else "decreasing"
                        }
                        logger.info("Cost Analyst using database data")
                    finally:
                        db.close()
                else:
                    # Fallback to mock data
                    dashboard_data = azure_data_generator.generate_dashboard_data()
                    cost_data = {
                        "total_monthly_cost": dashboard_data["total_monthly_cost"],
                        "monthly_change_percent": dashboard_data["monthly_change_percent"],
                        "daily_costs": dashboard_data["daily_costs"][-7:],  # Last 7 days
                        "top_services": dashboard_data["top_services"],
                        "cost_trend": "increasing" if dashboard_data["monthly_change_percent"] > 0 else "decreasing"
                    }
                    logger.info("Cost Analyst using mock data")

            # Try LLM first, fall back if unavailable
            if self.llm:
                try:
                    return await self._llm_analysis(cost_data, query)
                except Exception as llm_error:
                    logger.warning(f"LLM analysis failed, using fallback: {llm_error}")
                    return self._fallback_analysis(cost_data, query)
            else:
                return self._fallback_analysis(cost_data, query)

        except Exception as e:
            logger.error(f"Cost analysis failed: {e}")
            return f"Error during cost analysis: {str(e)}"

    async def _llm_analysis(self, cost_data: Dict[str, Any], query: str) -> str:
        """LLM-powered cost analysis"""
        total_cost = cost_data.get("total_monthly_cost", 0)
        change_percent = cost_data.get("monthly_change_percent", 0)
        top_services = cost_data.get("top_services", [])

        # Prepare context for LLM
        # Handle both dict and tuple formats for top_services
        if top_services and isinstance(top_services[0], dict):
            services_text = "\n".join([f"- {item['service']}: ${item['cost']:,.2f}" for item in top_services[:5]])
        else:
            services_text = "\n".join([f"- {service}: ${cost:,.2f}" for service, cost in top_services[:5]])

        prompt = f"""You are an Azure Cost Analyst AI. Analyze the following Azure cost data and answer the user's question.

**Current Azure Cost Data:**
- Total Monthly Cost: ${total_cost:,.2f}
- Monthly Change: {change_percent:+.1f}%
- Cost Trend: {"Increasing" if change_percent > 0 else "Decreasing"}

**Top Spending Services:**
{services_text}

**User Question:** {query}

Provide a detailed, professional analysis. Include:
1. Answer to the user's specific question
2. Key insights about the cost data
3. Specific recommendations for cost optimization
4. Any alerts or concerns about spending patterns

Keep the response concise but informative, using markdown formatting."""

        response = await self.llm.ainvoke(prompt)
        return response



    def _fallback_analysis(self, cost_data: Dict[str, Any], query: str) -> str:
        """Fallback analysis when LLM is unavailable"""
        total_cost = cost_data.get("total_monthly_cost", 0)
        change_percent = cost_data.get("monthly_change_percent", 0)
        top_services = cost_data.get("top_services", [])

        analysis = f"""**Azure Cost Analysis**

**Current Month Spending**: ${total_cost:,.2f}
**Monthly Change**: {change_percent:+.1f}%

**Top Spending Services**:
"""
        # Handle both dict and tuple formats for top_services
        for item in top_services[:3]:
            if isinstance(item, dict):
                service = item.get("service", "Unknown")
                cost = float(item.get("cost", 0))
            else:
                service, cost = item
                cost = float(cost)

            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            analysis += f"- {service}: ${cost:,.2f} ({percentage:.1f}% of total)\n"

        if change_percent > 10:
            analysis += f"\n⚠️ **Alert**: Costs have increased by {change_percent:.1f}% this month. Review top services for optimization opportunities."
        elif change_percent < -10:
            analysis += f"\n✓ **Good News**: Costs have decreased by {abs(change_percent):.1f}% this month."

        analysis += "\n\n**Recommendations**: Focus on optimizing the top 3 services which represent the majority of your Azure spending."

        return analysis


# Singleton instance
cost_analyst = CostAnalystAgent()
