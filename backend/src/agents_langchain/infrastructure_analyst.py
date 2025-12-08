"""Infrastructure Analyst Agent - Analyzes Azure resource utilization and optimization"""

from typing import Dict, Any, Optional
import logging

from src.mock.azure_data_generator import azure_data_generator
from src.config.settings import Settings
from src.config.database import SessionLocal
from src.repositories import VMRepository, StorageRepository

logger = logging.getLogger(__name__)
settings = Settings()


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
                if settings.USE_DATABASE:
                    # Get data from database
                    db = SessionLocal()
                    try:
                        vm_repo = VMRepository(db)
                        storage_repo = StorageRepository(db)

                        vm_summary = vm_repo.get_vms_summary()
                        vms = vm_repo.get_all_vms()
                        storage_summary = storage_repo.get_storage_summary()
                        storage_accounts = storage_repo.get_all_storage_accounts()

                        infrastructure_data = {
                            "virtual_machines": {
                                "total_instances": vm_summary["totalCount"],
                                "running_instances": vm_summary["runningCount"],
                                "stopped_instances": vm_summary["stoppedCount"],
                                "average_cpu": vm_summary["avgCpuUtilization"],
                                "average_memory": vm_summary["avgMemoryUtilization"],
                                "total_cost": vm_summary["totalMonthlyCost"],
                                "potential_savings": vm_summary["potentialSavings"],
                                "underutilized_vms": vm_summary.get("underutilizedVMs", []),
                                "vms": vms  # Include all VMs (will show sample by default, all when requested)
                            },
                            "storage_accounts": {
                                "total_accounts": storage_summary["totalCount"],
                                "total_size_gb": storage_summary["totalSizeGB"],
                                "total_cost": storage_summary["totalMonthlyCost"],
                                "potential_savings": storage_summary["potentialSavings"],
                                "tier_distribution": storage_summary.get("tierDistribution", {}),
                                "optimization_opportunities": storage_summary.get("optimizationOpportunities", [])[:5]
                            }
                        }
                        logger.info("Infrastructure Analyst using database data")
                    finally:
                        db.close()
                else:
                    # Fallback to mock data
                    analysis = azure_data_generator.generate_comprehensive_analysis()
                    infra = analysis.get("infrastructure_analysis", {})
                    infrastructure_data = {
                        "virtual_machines": infra.get("vm_analysis", {}),
                        "storage_accounts": infra.get("storage_analysis", {})
                    }
                    logger.info("Infrastructure Analyst using mock data")

            # Use fallback analysis
            return self._fallback_analysis(infrastructure_data, query)

        except Exception as e:
            logger.error(f"Infrastructure analysis failed: {e}")
            return f"Error during infrastructure analysis: {str(e)}"

    def _fallback_analysis(self, infrastructure_data: Dict[str, Any], query: str) -> str:
        """Fallback analysis when LLM is unavailable"""
        query_lower = query.lower()
        # Check if user wants to see ALL resources
        show_all_vms = any(word in query_lower for word in ['all vm', 'all virtual', 'every vm', 'list vm', 'show me all'])

        vm_data = infrastructure_data.get("virtual_machines", {})
        storage_data = infrastructure_data.get("storage_accounts", {})

        total_instances = vm_data.get("total_instances", 0)
        avg_cpu = vm_data.get("average_cpu", 0)
        vm_savings = vm_data.get("potential_savings", 0)
        storage_savings = storage_data.get("potential_savings", 0)

        analysis = f"""**Azure Infrastructure Analysis**

**Virtual Machines Overview**:
- Total Instances: {total_instances}
- Running: {vm_data.get("running_instances", 0)} | Stopped: {vm_data.get("stopped_instances", 0)}
- Average CPU Utilization: {avg_cpu:.1f}%
- Average Memory Utilization: {vm_data.get("average_memory", 0):.1f}%
- Monthly Cost: ${vm_data.get("total_cost", 0):,.2f}
- Potential Savings: ${vm_savings:,.2f}
"""

        # Show underutilized VMs if available
        underutilized = vm_data.get("underutilized_vms", [])
        if underutilized and not show_all_vms:
            analysis += f"\n**Underutilized VMs** (CPU < 30%):\n"
            for vm in underutilized[:3]:  # Top 3
                analysis += f"- {vm.get('name', 'N/A')} ({vm.get('size', 'N/A')}): CPU {vm.get('cpuUtilization', 0):.1f}% - Save ${vm.get('potentialSavings', 0):,.2f}/mo\n"

        # Show specific VMs if available
        vms = vm_data.get("vms", [])
        if vms:
            if show_all_vms:
                # Show ALL VMs when explicitly requested
                analysis += f"\n**All Virtual Machines** ({len(vms)} total):\n"
                for vm in vms:
                    status_emoji = "🟢" if vm.get("status") == "Running" else "🔴"
                    analysis += f"\n{status_emoji} **{vm.get('name', 'N/A')}** ({vm.get('size', 'N/A')})\n"
                    analysis += f"   - Status: {vm.get('status', 'N/A')} | CPU: {vm.get('cpuUtilization', 0):.1f}% | Memory: {vm.get('memoryUtilization', 0):.1f}%\n"
                    analysis += f"   - Cost: ${vm.get('monthlyCost', 0):,.2f}/mo | Location: {vm.get('location', 'N/A')}\n"
                    if vm.get('recommendation'):
                        analysis += f"   - Recommendation: {vm.get('recommendation')}\n"
            else:
                # Show sample VMs by default
                analysis += f"\n**Sample VMs** (showing {min(3, len(vms))} of {len(vms)}):\n"
                for vm in vms[:3]:
                    status_emoji = "🟢" if vm.get("status") == "Running" else "🔴"
                    analysis += f"{status_emoji} **{vm.get('name', 'N/A')}** ({vm.get('size', 'N/A')})\n"
                    analysis += f"   - Status: {vm.get('status', 'N/A')} | CPU: {vm.get('cpuUtilization', 0):.1f}% | Memory: {vm.get('memoryUtilization', 0):.1f}%\n"
                    analysis += f"   - Cost: ${vm.get('monthlyCost', 0):,.2f}/mo | Location: {vm.get('location', 'N/A')}\n"

        analysis += f"""
**Storage Accounts Overview**:
- Total Accounts: {storage_data.get("total_accounts", 0)}
- Total Size: {storage_data.get("total_size_gb", 0):,.2f} GB
- Monthly Cost: ${storage_data.get("total_cost", 0):,.2f}
- Potential Savings: ${storage_savings:,.2f}
"""

        # Show tier distribution
        tier_dist = storage_data.get("tier_distribution", {})
        if tier_dist:
            analysis += "\n**Tier Distribution**:\n"
            for tier, count in tier_dist.items():
                analysis += f"- {tier}: {count} account(s)\n"

        # Show optimization opportunities
        opt_opps = storage_data.get("optimization_opportunities", [])
        if opt_opps:
            analysis += f"\n**Storage Optimization Opportunities** ({len(opt_opps)} accounts):\n"
            for storage in opt_opps[:2]:  # Top 2
                analysis += f"- {storage.get('name', 'N/A')}: Move from {storage.get('tier', 'N/A')} to {storage.get('recommendedTier', 'N/A')} - Save ${storage.get('potentialSavings', 0):,.2f}/mo\n"

        analysis += "\n**Key Recommendations**:\n"

        if avg_cpu < 40:
            analysis += f"- 🎯 **VM Right-Sizing**: Average CPU is {avg_cpu:.1f}%. Review underutilized VMs for downsizing.\n"

        if vm_savings > 0:
            analysis += f"- 💰 **VM Optimization**: ${vm_savings:,.2f}/month savings available from VM optimization.\n"

        if storage_savings > 0:
            analysis += f"- 📦 **Storage Optimization**: ${storage_savings:,.2f}/month savings from tier optimization.\n"

        total_potential = vm_savings + storage_savings
        analysis += f"\n**Total Potential Monthly Savings**: ${total_potential:,.2f}"

        return analysis


# Singleton instance
infrastructure_analyst = InfrastructureAnalystAgent()
