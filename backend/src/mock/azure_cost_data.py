"""Azure Cost Management mock data generator"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import random


class CostDataGenerator:
    """
    Generates realistic Azure Cost Management data

    Simulates Azure Cost Management API responses with realistic
    cost patterns, daily variations, and service breakdowns.
    """

    # Azure service names and typical cost ranges (min, max per month)
    AZURE_SERVICES = {
        "Virtual Machines": (3000, 6000),
        "Azure SQL Database": (2000, 4000),
        "Storage Accounts": (1500, 3000),
        "App Services": (1000, 2500),
        "Azure Kubernetes Service": (800, 2000),
        "Azure Functions": (200, 600),
        "Azure CDN": (300, 800),
        "Application Gateway": (400, 900),
        "Virtual Network": (200, 500),
        "Azure Monitor": (150, 400)
    }

    def generate_daily_costs(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Generate daily cost data with realistic patterns

        Args:
            days: Number of days of history to generate

        Returns:
            List of daily cost records with date and cost

        Patterns:
        - Weekdays: Normal spending
        - Weekends: 20-30% reduction
        - Month-end: Slight increase
        - Random variations: ±15%
        """
        costs = []
        base_daily_cost = 400  # ~$12k per month

        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).date()
            day_of_week = date.weekday()
            day_of_month = date.day

            # Weekend pattern (Sat=5, Sun=6)
            if day_of_week >= 5:
                multiplier = random.uniform(0.7, 0.8)
            # Month-end spike (days 28-31)
            elif day_of_month >= 28:
                multiplier = random.uniform(1.05, 1.15)
            # Normal weekday with variation
            else:
                multiplier = random.uniform(0.90, 1.10)

            daily_cost = base_daily_cost * multiplier

            costs.append({
                "date": date.isoformat(),
                "cost": round(daily_cost, 2),
                "day_of_week": date.strftime("%A")
            })

        return costs

    def generate_service_costs(self) -> List[List[Any]]:
        """
        Generate top Azure services by cost

        Returns:
            List of [service_name, cost] tuples sorted by cost
        """
        services = []

        for service_name, (min_cost, max_cost) in self.AZURE_SERVICES.items():
            cost = round(random.uniform(min_cost, max_cost), 2)
            services.append([service_name, cost])

        # Sort by cost descending and return top 5
        services.sort(key=lambda x: x[1], reverse=True)
        return services[:5]

    def generate_resource_group_costs(self, rg_count: int = 4) -> List[Dict[str, Any]]:
        """
        Generate resource group cost breakdown

        Args:
            rg_count: Number of resource groups to generate

        Returns:
            List of resource group cost data
        """
        rg_names = ["production", "staging", "development", "shared-services", "networking"]
        locations = ["eastus", "westus2", "westeurope", "southeastasia"]

        resource_groups = []

        for i in range(min(rg_count, len(rg_names))):
            rg_name = rg_names[i]

            # Production typically costs more
            if rg_name == "production":
                cost = round(random.uniform(6000, 10000), 2)
                resource_count = random.randint(30, 60)
            elif rg_name == "staging":
                cost = round(random.uniform(2000, 4000), 2)
                resource_count = random.randint(15, 30)
            else:
                cost = round(random.uniform(500, 2000), 2)
                resource_count = random.randint(5, 20)

            resource_groups.append({
                "name": f"rg-{rg_name}",
                "cost": cost,
                "resourceCount": resource_count,
                "location": random.choice(locations),
                "tags": {
                    "environment": rg_name if rg_name in ["production", "staging", "development"] else "shared",
                    "managed-by": "terraform",
                    "cost-center": f"cc-{random.randint(1000, 9999)}"
                }
            })

        return resource_groups

    def generate_cost_trend(self, days: int = 30) -> str:
        """
        Determine overall cost trend

        Args:
            days: Days to analyze

        Returns:
            Trend description: "increasing", "decreasing", or "stable"
        """
        trend_rand = random.random()

        if trend_rand > 0.6:
            return "increasing"
        elif trend_rand > 0.3:
            return "stable"
        else:
            return "decreasing"


# Singleton instance
cost_data_generator = CostDataGenerator()
