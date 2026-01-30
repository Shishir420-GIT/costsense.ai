"""Financial Analyst Agent - Performs ROI calculations and financial projections"""

from typing import Dict, Any, Optional
import logging
import random

from src.mock.azure_data_generator import azure_data_generator

logger = logging.getLogger(__name__)


class FinancialAnalystAgent:
    """
    Specialized agent for financial analysis and ROI calculations

    Responsibilities:
    - Calculate ROI for optimization initiatives
    - Perform cost-benefit analysis
    - Project future costs
    - Assess payback periods
    - Risk assessment for changes
    """

    def __init__(self):
        """Initialize the financial analyst agent"""
        logger.info("Financial Analyst Agent initialized")

    async def analyze(self, query: str, financial_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Perform financial analysis

        Args:
            query: User's financial question
            financial_data: Optional financial data (calculated if not provided)

        Returns:
            Detailed financial analysis response
        """
        try:
            # Calculate financial data if not provided
            if financial_data is None:
                financial_data = self._calculate_financial_metrics()

            # Use fallback analysis
            return self._fallback_analysis(financial_data, query)

        except Exception as e:
            logger.error(f"Financial analysis failed: {e}")
            return f"Error during financial analysis: {str(e)}"

    def _calculate_financial_metrics(self) -> Dict[str, Any]:
        """Calculate financial metrics from mock data"""
        analysis = azure_data_generator.generate_comprehensive_analysis()

        current_monthly_cost = analysis["cost_analysis"]["total_cost"]
        potential_savings = analysis["financial_analysis"]["total_potential_savings"]

        # Calculate metrics
        annual_current_cost = current_monthly_cost * 12
        annual_savings = potential_savings * 12
        implementation_cost = potential_savings * 0.5  # Assume 50% of monthly savings

        roi_percentage = ((annual_savings - implementation_cost) / implementation_cost) * 100 if implementation_cost > 0 else 0
        payback_months = implementation_cost / potential_savings if potential_savings > 0 else 0

        return {
            "current_monthly_cost": round(current_monthly_cost, 2),
            "potential_monthly_savings": round(potential_savings, 2),
            "annual_current_cost": round(annual_current_cost, 2),
            "annual_savings": round(annual_savings, 2),
            "estimated_implementation_cost": round(implementation_cost, 2),
            "roi_percentage": round(roi_percentage, 1),
            "payback_period_months": round(payback_months, 1),
            "confidence_level": random.randint(80, 95),
            "projected_6_month_cost": {
                "without_optimization": round(current_monthly_cost * 6, 2),
                "with_optimization": round((current_monthly_cost - potential_savings) * 6, 2),
                "net_savings": round(potential_savings * 6 - implementation_cost, 2)
            }
        }

    def _fallback_analysis(self, financial_data: Dict[str, Any], query: str) -> str:
        """Fallback analysis when LLM is unavailable"""
        current_cost = financial_data.get("current_monthly_cost", 0)
        savings = financial_data.get("potential_monthly_savings", 0)
        roi = financial_data.get("roi_percentage", 0)
        payback = financial_data.get("payback_period_months", 0)
        confidence = financial_data.get("confidence_level", 85)

        analysis = f"""**Azure Financial Analysis**

**Current State**:
- Monthly Cost: ${current_cost:,.2f}
- Annual Cost: ${current_cost * 12:,.2f}

**Optimization Potential**:
- Monthly Savings: ${savings:,.2f}
- Annual Savings: ${savings * 12:,.2f}
- Savings Percentage: {(savings/current_cost*100):.1f}%

**ROI Metrics**:
- Return on Investment: {roi:.1f}%
- Payback Period: {payback:.1f} months
- Confidence Level: {confidence}%

**6-Month Projection**:
- Without Optimization: ${current_cost * 6:,.2f}
- With Optimization: ${(current_cost - savings) * 6:,.2f}
- Net Savings: ${savings * 6:,.2f}

**Recommendation**: """

        if roi > 150:
            analysis += f"**Highly Recommended** - Excellent ROI of {roi:.1f}% with quick payback period of {payback:.1f} months."
        elif roi > 100:
            analysis += f"**Recommended** - Good ROI of {roi:.1f}% with reasonable payback period."
        else:
            analysis += f"**Consider Carefully** - Moderate ROI of {roi:.1f}%. Review specific optimizations for best value."

        return analysis


# Singleton instance
financial_analyst = FinancialAnalystAgent()
