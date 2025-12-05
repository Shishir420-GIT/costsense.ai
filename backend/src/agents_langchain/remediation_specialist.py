"""Remediation Specialist Agent - Creates actionable implementation plans"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class RemediationSpecialistAgent:
    """
    Specialized agent for creating remediation plans

    Responsibilities:
    - Generate step-by-step implementation plans
    - Prioritize optimization actions
    - Assess complexity and time requirements
    - Provide rollback procedures
    - Create actionable checklists
    """

    def __init__(self):
        """Initialize the remediation specialist agent"""
        logger.info("Remediation Specialist Agent initialized")

    async def create_plan(self, query: str, recommendations: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Create remediation plan

        Args:
            query: User's remediation question
            recommendations: Optional list of recommendations (generated if not provided)

        Returns:
            Detailed remediation plan
        """
        try:
            # Generate recommendations if not provided
            if recommendations is None:
                recommendations = self._generate_recommendations()

            # Use fallback plan
            return self._fallback_plan(recommendations)

        except Exception as e:
            logger.error(f"Remediation planning failed: {e}")
            return f"Error creating remediation plan: {str(e)}"

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations from mock data"""
        from src.mock.azure_data_generator import azure_data_generator

        vm_data = azure_data_generator.vm_gen.generate()
        storage_data = azure_data_generator.storage_gen.generate()

        recommendations = []

        # VM recommendations
        for vm in vm_data["instances"]:
            if vm["potentialSavings"] > 0 and vm["recommendation"] != "Optimal sizing":
                recommendations.append({
                    "priority": "High" if vm["potentialSavings"] > 50 else "Medium",
                    "category": "Compute",
                    "resource": vm["name"],
                    "current_state": f"{vm['size']} ({vm['status']})",
                    "recommendation": vm["recommendation"],
                    "savings": vm["potentialSavings"],
                    "complexity": "Low" if "downsize" in vm["recommendation"].lower() else "Medium",
                    "estimated_time": "15-30 minutes"
                })

        # Storage recommendations
        for storage in storage_data["accounts"]:
            if storage["potentialSavings"] > 0:
                for rec in storage["recommendations"]:
                    if rec != "Already optimized":
                        recommendations.append({
                            "priority": "Medium",
                            "category": "Storage",
                            "resource": storage["name"],
                            "current_state": f"{storage['tier']} tier, {storage['sizeGB']} GB",
                            "recommendation": rec,
                            "savings": storage["potentialSavings"] / len(storage["recommendations"]),
                            "complexity": "Low",
                            "estimated_time": "10-20 minutes"
                        })

        # Sort by savings (highest first)
        recommendations.sort(key=lambda x: x["savings"], reverse=True)

        return recommendations[:10]  # Top 10 recommendations

    def _fallback_plan(self, recommendations: List[Dict[str, Any]]) -> str:
        """Fallback plan when LLM is unavailable"""
        if not recommendations:
            recommendations = self._generate_recommendations()

        total_savings = sum(r.get("savings", 0) for r in recommendations)

        plan = f"""**Azure Cost Optimization Remediation Plan**

**Total Potential Savings**: ${total_savings:,.2f}/month

**Prioritized Actions**:

"""

        # Group by priority
        high_priority = [r for r in recommendations if r.get("priority") == "High"]
        medium_priority = [r for r in recommendations if r.get("priority") == "Medium"]
        low_priority = [r for r in recommendations if r.get("priority") == "Low"]

        if high_priority:
            plan += "**🔴 HIGH PRIORITY** (Implement First):\n\n"
            for i, rec in enumerate(high_priority, 1):
                plan += f"{i}. **{rec['resource']}** ({rec['category']})\n"
                plan += f"   - Action: {rec['recommendation']}\n"
                plan += f"   - Savings: ${rec['savings']:.2f}/month\n"
                plan += f"   - Time: {rec['estimated_time']}\n"
                plan += f"   - Complexity: {rec['complexity']}\n\n"

        if medium_priority:
            plan += "**🟡 MEDIUM PRIORITY** (Implement After High):\n\n"
            for i, rec in enumerate(medium_priority, 1):
                plan += f"{i}. **{rec['resource']}** ({rec['category']})\n"
                plan += f"   - Action: {rec['recommendation']}\n"
                plan += f"   - Savings: ${rec['savings']:.2f}/month\n\n"

        plan += "\n**Implementation Best Practices**:\n"
        plan += "1. Test in non-production environment first\n"
        plan += "2. Take snapshots/backups before making changes\n"
        plan += "3. Implement during maintenance windows\n"
        plan += "4. Monitor performance metrics after changes\n"
        plan += "5. Document all changes in your change management system\n"

        return plan


# Singleton instance
remediation_specialist = RemediationSpecialistAgent()
