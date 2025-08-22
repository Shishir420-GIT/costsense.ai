import asyncio
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import random

class CostOptimizationOrchestrator:
    def __init__(self):
        self.settings = {"OLLAMA_HOST": "localhost", "OLLAMA_MODEL": "llama2"}
    
    async def analyze_costs(self, user_query: str) -> str:
        """Simple mock cost analysis"""
        await asyncio.sleep(0.1)  # Simulate processing
        return f"Cost analysis complete for: {user_query}. Found optimization opportunities."
    
    async def parallel_analysis(self, user_query: str) -> Dict[str, str]:
        """Mock parallel analysis"""
        await asyncio.sleep(0.2)
        return {
            "cost_analysis": "Cost trends show 15% increase in EC2 spending",
            "infrastructure_analysis": "Found 3 oversized instances and 2 unused volumes",
            "financial_analysis": "Potential monthly savings: $2,340",
            "remediation": "Recommend rightsizing instances and implementing scheduled scaling"
        }
    
    async def comprehensive_analysis(self, user_query: str) -> Dict[str, Any]:
        """Mock comprehensive analysis with realistic data"""
        await asyncio.sleep(0.3)
        
        # Generate mock EC2 data
        ec2_instances = []
        instance_types = ["t3.micro", "t3.small", "t3.medium", "m5.large", "c5.xlarge"]
        recommendations = ["Optimal", "Downsize", "Consider Reserved", "Terminate"]
        
        for i in range(4):
            ec2_instances.append({
                "instance_id": f"i-{random.randint(100000000, 999999999)}",
                "instance_type": random.choice(instance_types),
                "avg_cpu_utilization": round(random.uniform(15, 95), 1),
                "memory_utilization": round(random.uniform(20, 85), 1),
                "recommendation": random.choice(recommendations),
                "monthly_cost": round(random.uniform(20, 200), 2),
                "potential_savings": round(random.uniform(5, 50), 2)
            })
        
        # Generate mock cost data
        daily_costs = []
        base_cost = 1000
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
            cost = base_cost + random.uniform(-100, 150)
            daily_costs.append({"date": date, "cost": round(cost, 2)})
        
        top_services = [
            ["EC2-Instance", round(random.uniform(800, 1200), 2)],
            ["S3", round(random.uniform(200, 400), 2)],
            ["RDS", round(random.uniform(300, 600), 2)],
            ["Lambda", round(random.uniform(50, 150), 2)],
            ["CloudFront", round(random.uniform(100, 300), 2)]
        ]
        
        return {
            "cost_analysis": {
                "total_cost": sum(service[1] for service in top_services),
                "daily_costs": daily_costs,
                "top_services": top_services,
                "cost_trend": "increasing",
                "variance_percentage": 12.5
            },
            "infrastructure_analysis": {
                "ec2_analysis": {
                    "total_instances": len(ec2_instances),
                    "instances": ec2_instances,
                    "potential_monthly_savings": sum(inst["potential_savings"] for inst in ec2_instances),
                    "avg_utilization": round(sum(inst["avg_cpu_utilization"] for inst in ec2_instances) / len(ec2_instances), 1)
                },
                "s3_analysis": {
                    "buckets": [
                        {"name": "data-backup", "size_gb": 1024, "cost": 23.04, "optimization": "lifecycle"},
                        {"name": "logs-archive", "size_gb": 2048, "cost": 46.08, "optimization": "compression"}
                    ]
                }
            },
            "financial_analysis": {
                "total_potential_savings": sum(inst["potential_savings"] for inst in ec2_instances) + 69.12,
                "roi_percentage": 185,
                "payback_period_months": 2.1,
                "confidence_level": 88
            },
            "remediation_plan": [
                "Implement auto-scaling for EC2 instances during off-peak hours",
                "Set up S3 lifecycle policies for cost optimization",
                "Consider Reserved Instances for consistent workloads",
                "Enable detailed monitoring and alerting"
            ],
            "timestamp": datetime.now().isoformat()
        }

# Global instance
orchestrator = CostOptimizationOrchestrator()