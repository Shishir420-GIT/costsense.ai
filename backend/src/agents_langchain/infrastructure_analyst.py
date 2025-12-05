"""Infrastructure Analyst Agent - Analyzes Azure resource utilization and optimization"""

from typing import Dict, Any, Optional
import logging

from src.mock.azure_data_generator import azure_data_generator

logger = logging.getLogger(__name__)


class InfrastructureAnalystAgent:
    """
    Specialized agent for Azure infrastructure analysis

    Responsibilities:
    - Analyze VM utilization and sizing
    - Identify right-sizing opportunities
    - Optimize storage tiers
    - Recommend Reserved Instances
    - Assess resource efficiency
    """

    def __init__(self):
        """Initialize the infrastructure analyst agent"""
        logger.info("Infrastructure Analyst Agent initialized")

    async def analyze(self, query: str, infrastructure_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Perform infrastructure analysis

        Args:
            query: User's infrastructure question
            infrastructure_data: Optional infrastructure data (calculated if not provided)

        Returns:
            Detailed infrastructure analysis response
        """
        try:
            # Calculate infrastructure data if not provided
            if infrastructure_data is None:
                analysis = azure_data_generator.generate_comprehensive_analysis()
                infra = analysis.get("infrastructure_analysis", {})
                infrastructure_data = {
                    "virtual_machines": infra.get("vm_analysis", {}),
                    "storage_accounts": infra.get("storage_analysis", {})
                }

            # Use fallback analysis
            return self._fallback_analysis(infrastructure_data, query)

        except Exception as e:
            logger.error(f"Infrastructure analysis failed: {e}")
            return f"Error during infrastructure analysis: {str(e)}"

    def _fallback_analysis(self, infrastructure_data: Dict[str, Any], query: str) -> str:
        """Fallback analysis when LLM is unavailable"""
        vm_data = infrastructure_data.get("virtual_machines", {})
        storage_data = infrastructure_data.get("storage_accounts", {})

        total_instances = vm_data.get("total_instances", 0)
        avg_cpu = vm_data.get("average_cpu", 0)
        vm_savings = vm_data.get("potential_savings", 0)
        storage_savings = storage_data.get("potential_savings", 0)

        analysis = f"""**Azure Infrastructure Analysis**

**Virtual Machines**:
- Total Instances: {total_instances}
- Running Instances: {vm_data.get("running_instances", 0)}
- Average CPU Utilization: {avg_cpu:.1f}%
- Monthly Cost: ${vm_data.get("total_cost", 0):,.2f}
- Potential Savings: ${vm_savings:,.2f}

**Storage Accounts**:
- Total Accounts: {storage_data.get("total_accounts", 0)}
- Total Size: {storage_data.get("total_size_gb", 0):,} GB
- Monthly Cost: ${storage_data.get("total_cost", 0):,.2f}
- Potential Savings: ${storage_savings:,.2f}

**Key Recommendations**:
"""

        if avg_cpu < 40:
            analysis += f"- 🎯 **VM Right-Sizing**: Average CPU utilization is {avg_cpu:.1f}%. Consider downsizing underutilized VMs.\n"

        if vm_savings > 0:
            analysis += f"- 💰 **Immediate Opportunity**: ${vm_savings:,.2f}/month savings from VM optimization.\n"

        if storage_savings > 0:
            analysis += f"- 📦 **Storage Optimization**: ${storage_savings:,.2f}/month savings from tier optimization and lifecycle policies.\n"

        total_potential = vm_savings + storage_savings
        analysis += f"\n**Total Potential Monthly Savings**: ${total_potential:,.2f}"

        return analysis


# Singleton instance
infrastructure_analyst = InfrastructureAnalystAgent()
