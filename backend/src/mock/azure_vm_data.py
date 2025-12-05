"""Azure Virtual Machines mock data generator"""

from typing import Dict, Any, List
import random


class VMDataGenerator:
    """
    Generates realistic Azure VM data

    Simulates Azure Virtual Machines with utilization metrics,
    recommendations, and cost data.
    """

    # Azure VM sizes with typical monthly costs (USD)
    VM_SIZES = {
        "Standard_B1s": 7.59,
        "Standard_B2s": 30.37,
        "Standard_B4ms": 121.47,
        "Standard_D2s_v3": 96.36,
        "Standard_D4s_v3": 192.72,
        "Standard_D8s_v3": 385.44,
        "Standard_E2s_v3": 109.50,
        "Standard_E4s_v3": 219.00,
        "Standard_F2s_v2": 76.65,
        "Standard_F4s_v2": 153.30,
    }

    VM_WORKLOAD_TYPES = ["web", "api", "worker", "database", "cache", "jumpbox"]
    LOCATIONS = ["eastus", "westus2", "westeurope", "southeastasia", "canadacentral"]
    STATUSES = ["running", "stopped", "deallocated"]

    def generate(self, instance_count: int = None) -> Dict[str, Any]:
        """
        Generate VM instance data

        Args:
            instance_count: Number of VMs to generate (random 6-12 if None)

        Returns:
            Dictionary with VM instances and metrics
        """
        if instance_count is None:
            instance_count = random.randint(6, 12)

        instances = []

        for i in range(instance_count):
            instance = self._generate_single_vm(i)
            instances.append(instance)

        # Calculate totals
        total_monthly_cost = sum(vm["monthlyCost"] for vm in instances)
        potential_savings = sum(vm["potentialSavings"] for vm in instances)
        running_instances = sum(1 for vm in instances if vm["status"] == "running")

        return {
            "totalInstances": len(instances),
            "runningInstances": running_instances,
            "instances": instances,
            "totalMonthlyCost": round(total_monthly_cost, 2),
            "potentialSavings": round(potential_savings, 2),
            "averageCpuUtilization": round(
                sum(vm["cpuUtilization"] for vm in instances) / len(instances), 1
            )
        }

    def _generate_single_vm(self, index: int) -> Dict[str, Any]:
        """Generate a single VM instance"""

        # Select random VM size
        vm_size = random.choice(list(self.VM_SIZES.keys()))
        base_cost = self.VM_SIZES[vm_size]

        # Generate utilization
        cpu_util = round(random.uniform(15, 95), 1)
        memory_util = round(random.uniform(25, 90), 1)

        # Determine status (90% running, 10% stopped/deallocated)
        status_rand = random.random()
        if status_rand > 0.9:
            status = random.choice(["stopped", "deallocated"])
            cpu_util = 0
            memory_util = 0
        else:
            status = "running"

        # Generate recommendation based on utilization
        recommendation, potential_savings = self._generate_recommendation(
            cpu_util, memory_util, vm_size, base_cost, status
        )

        # Monthly cost (stopped VMs still incur storage costs)
        if status == "deallocated":
            monthly_cost = round(base_cost * 0.1, 2)  # Only storage
        elif status == "stopped":
            monthly_cost = round(base_cost * 0.2, 2)  # Storage + some compute
        else:
            monthly_cost = round(base_cost * random.uniform(0.95, 1.05), 2)

        # Generate workload type
        workload = random.choice(self.VM_WORKLOAD_TYPES)

        # Generate resource group based on index
        if index < 3:
            rg = "rg-production"
        elif index < 6:
            rg = "rg-staging"
        else:
            rg = "rg-development"

        return {
            "id": f"/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/vm-{workload}-{index:02d}",
            "name": f"vm-{workload}-{index:02d}",
            "size": vm_size,
            "location": random.choice(self.LOCATIONS),
            "resourceGroup": rg,
            "status": status,
            "cpuUtilization": cpu_util,
            "memoryUtilization": memory_util,
            "monthlyCost": monthly_cost,
            "recommendation": recommendation,
            "potentialSavings": potential_savings,
            "tags": {
                "environment": rg.split("-")[1],
                "workload": workload,
                "managed-by": "terraform"
            }
        }

    def _generate_recommendation(
        self,
        cpu_util: float,
        memory_util: float,
        vm_size: str,
        base_cost: float,
        status: str
    ) -> tuple[str, float]:
        """
        Generate optimization recommendation

        Returns:
            Tuple of (recommendation text, potential savings)
        """
        if status in ["stopped", "deallocated"]:
            if random.random() > 0.5:
                return "Consider deleting if no longer needed", round(base_cost * 0.9, 2)
            else:
                return "Deallocated - no action needed", 0

        # Both CPU and memory low
        if cpu_util < 30 and memory_util < 40:
            savings = round(base_cost * 0.5, 2)
            return "Downsize to smaller VM tier", savings

        # CPU low
        elif cpu_util < 40:
            savings = round(base_cost * 0.3, 2)
            return "Consider right-sizing to lower tier", savings

        # High utilization
        elif cpu_util > 85 or memory_util > 85:
            return "Consider scaling up or adding instances", 0

        # Optimal range (40-80% CPU, 40-85% memory)
        else:
            # 20% chance to recommend reserved instance
            if random.random() > 0.8:
                savings = round(base_cost * 0.3, 2)
                return "Consider Reserved Instance for long-term savings", savings
            else:
                return "Optimal sizing", 0


# Singleton instance
vm_data_generator = VMDataGenerator()
