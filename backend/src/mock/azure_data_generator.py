"""Main Azure mock data generator orchestrator"""

from typing import Dict, Any
from datetime import datetime
import random
from .azure_cost_data import cost_data_generator
from .azure_vm_data import vm_data_generator
from .azure_storage_data import storage_data_generator


class AzureMockDataGenerator:
    """
    Master orchestrator for all Azure mock data generation

    Coordinates all specialized generators to produce comprehensive
    Azure cost and resource data for development and testing.
    """

    def __init__(self):
        """Initialize with all specialized generators"""
        self.cost_gen = cost_data_generator
        self.vm_gen = vm_data_generator
        self.storage_gen = storage_data_generator

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate complete dashboard summary data

        Returns:
            Comprehensive dashboard data with costs, trends, and metrics
        """
        # Generate daily costs
        daily_costs = self.cost_gen.generate_daily_costs(days=30)

        # Calculate total monthly cost
        total_monthly_cost = sum(day["cost"] for day in daily_costs)

        # Generate last month cost (for comparison)
        last_month_daily = self.cost_gen.generate_daily_costs(days=30)
        last_month_cost = sum(day["cost"] for day in last_month_daily)

        # Calculate change percentage
        monthly_change = ((total_monthly_cost - last_month_cost) / last_month_cost) * 100

        # Project month-end cost
        days_in_month = 30
        days_elapsed = len(daily_costs)
        avg_daily_cost = total_monthly_cost / days_elapsed
        projected_cost = avg_daily_cost * days_in_month

        return {
            "total_monthly_cost": round(total_monthly_cost, 2),
            "monthly_change_percent": round(monthly_change, 1),
            "projected_monthly_cost": round(projected_cost, 2),
            "daily_costs": daily_costs,
            "top_services": self.cost_gen.generate_service_costs(),
            "resource_groups": self.cost_gen.generate_resource_group_costs(),
            "utilization_metrics": {
                "compute": round(random.uniform(45, 85), 1),
                "storage": round(random.uniform(60, 90), 1),
                "database": round(random.uniform(55, 80), 1),
                "network": round(random.uniform(40, 70), 1)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive analysis data (replaces orchestrator_agent_simple)

        Returns:
            Complete analysis with all resource types and recommendations
        """
        vm_data = self.vm_gen.generate()
        storage_data = self.storage_gen.generate()
        daily_costs = self.cost_gen.generate_daily_costs(days=30)
        service_costs = self.cost_gen.generate_service_costs()

        # Calculate total potential savings
        total_savings = (
            vm_data.get("potentialSavings", 0) +
            storage_data.get("potentialSavings", 0)
        )

        # Calculate ROI
        roi_percentage = round(random.uniform(150, 250), 0)
        payback_months = round(random.uniform(1.5, 3.5), 1)
        confidence = round(random.uniform(80, 95), 0)

        return {
            "cost_analysis": {
                "total_cost": round(sum(day["cost"] for day in daily_costs), 2),
                "daily_costs": daily_costs,
                "top_services": service_costs,
                "cost_trend": self.cost_gen.generate_cost_trend(),
                "variance_percentage": round(random.uniform(5, 20), 1)
            },
            "infrastructure_analysis": {
                "vm_analysis": vm_data,
                "storage_analysis": storage_data
            },
            "financial_analysis": {
                "total_potential_savings": round(total_savings, 2),
                "roi_percentage": roi_percentage,
                "payback_period_months": payback_months,
                "confidence_level": confidence
            },
            "remediation_plan": [
                "Implement Azure VM auto-shutdown schedules for non-production resources",
                "Configure Azure Storage lifecycle management policies",
                "Right-size underutilized VMs based on CPU and memory metrics",
                "Consider Azure Reserved VM Instances for consistent workloads",
                "Enable Azure Advisor cost recommendations",
                "Implement resource tagging strategy for better cost allocation",
                "Set up Azure Cost Management budgets and alerts"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }


# Singleton instance
azure_data_generator = AzureMockDataGenerator()
