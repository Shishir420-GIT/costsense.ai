"""Azure Storage Accounts mock data generator"""

from typing import Dict, Any, List
import random


class StorageDataGenerator:
    """
    Generates realistic Azure Storage Account data

    Simulates storage accounts with different tiers, sizes,
    replication options, and optimization recommendations.
    """

    # Storage pricing per GB per month (approximate USD)
    TIER_PRICING = {
        "Hot": 0.0208,
        "Cool": 0.0152,
        "Archive": 0.00099
    }

    REPLICATION_TYPES = ["LRS", "GRS", "RA-GRS", "ZRS"]
    LOCATIONS = ["eastus", "westus2", "westeurope", "southeastasia"]
    ACCOUNT_TYPES = ["backup", "logs", "static", "data", "media", "archives"]

    def generate(self, account_count: int = None) -> Dict[str, Any]:
        """
        Generate storage account data

        Args:
            account_count: Number of accounts to generate (random 4-8 if None)

        Returns:
            Dictionary with storage accounts and metrics
        """
        if account_count is None:
            account_count = random.randint(4, 8)

        accounts = []

        for i in range(account_count):
            account = self._generate_single_account(i)
            accounts.append(account)

        # Calculate totals
        total_size = sum(acc["sizeGB"] for acc in accounts)
        total_cost = sum(acc["monthlyCost"] for acc in accounts)
        potential_savings = sum(acc["potentialSavings"] for acc in accounts)

        return {
            "totalAccounts": len(accounts),
            "accounts": accounts,
            "totalSizeGB": total_size,
            "totalMonthlyCost": round(total_cost, 2),
            "potentialSavings": round(potential_savings, 2)
        }

    def _generate_single_account(self, index: int) -> Dict[str, Any]:
        """Generate a single storage account"""

        # Account type determines typical size and tier
        account_type = random.choice(self.ACCOUNT_TYPES)

        # Size patterns by type
        if account_type == "backup":
            size_gb = random.randint(1000, 5000)
            tier = "Cool" if random.random() > 0.3 else "Hot"
        elif account_type == "logs":
            size_gb = random.randint(500, 3000)
            tier = "Hot" if random.random() > 0.5 else "Cool"
        elif account_type == "archives":
            size_gb = random.randint(2000, 10000)
            tier = "Archive" if random.random() > 0.4 else "Cool"
        elif account_type == "static":
            size_gb = random.randint(100, 500)
            tier = "Hot"
        else:  # data, media
            size_gb = random.randint(500, 2500)
            tier = random.choice(["Hot", "Cool"])

        # Calculate cost
        cost_per_gb = self.TIER_PRICING[tier]
        monthly_cost = size_gb * cost_per_gb

        # Add replication overhead (1.5x for GRS, 2x for RA-GRS)
        replication = random.choice(self.REPLICATION_TYPES)
        if replication == "GRS":
            monthly_cost *= 1.5
        elif replication == "RA-GRS":
            monthly_cost *= 2

        # Generate recommendations
        recommendations, potential_savings = self._generate_recommendations(
            account_type, tier, size_gb, monthly_cost, replication
        )

        # Generate name (storage account names must be lowercase, no hyphens)
        name = f"st{account_type}{index:02d}{random.randint(100, 999)}"

        return {
            "name": name,
            "location": random.choice(self.LOCATIONS),
            "tier": tier,
            "replication": replication,
            "sizeGB": size_gb,
            "monthlyCost": round(monthly_cost, 2),
            "accountType": account_type,
            "recommendations": recommendations,
            "potentialSavings": round(potential_savings, 2),
            "resourceGroup": f"rg-{account_type}-storage",
            "tags": {
                "purpose": account_type,
                "managed-by": "terraform"
            }
        }

    def _generate_recommendations(
        self,
        account_type: str,
        tier: str,
        size_gb: int,
        monthly_cost: float,
        replication: str
    ) -> tuple[List[str], float]:
        """Generate optimization recommendations"""

        recommendations = []
        total_savings = 0

        # Backup data should be in Cool or Archive
        if account_type == "backup" and tier == "Hot":
            recommendations.append("Move to Cool or Archive tier for backups")
            savings = monthly_cost * 0.4
            total_savings += savings

        # Logs older than 30 days should be Cool
        if account_type == "logs" and tier == "Hot" and size_gb > 1000:
            recommendations.append("Implement lifecycle policy to move old logs to Cool tier")
            savings = monthly_cost * 0.25
            total_savings += savings

        # Archives should be in Archive tier
        if account_type == "archives" and tier != "Archive":
            recommendations.append("Move to Archive tier for long-term storage")
            savings = monthly_cost * 0.6
            total_savings += savings

        # Large storage with RA-GRS might not need read access
        if replication == "RA-GRS" and random.random() > 0.7:
            recommendations.append("Consider GRS instead of RA-GRS if read access not required")
            savings = monthly_cost * 0.15
            total_savings += savings

        # Lifecycle management for large accounts
        if size_gb > 2000 and len(recommendations) == 0:
            recommendations.append("Implement lifecycle management policies")
            savings = monthly_cost * 0.15
            total_savings += savings

        # If no recommendations
        if len(recommendations) == 0:
            recommendations.append("Already optimized")

        return recommendations, total_savings


# Singleton instance
storage_data_generator = StorageDataGenerator()
