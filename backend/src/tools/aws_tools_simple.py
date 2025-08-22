import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any

class AWSCostExplorerTool:
    def _run(self, time_period: str = "30_days") -> str:
        """Mock AWS Cost Explorer data"""
        # Generate mock daily costs
        days = {"7_days": 7, "30_days": 30, "90_days": 90, "1_year": 365}.get(time_period, 30)
        
        daily_costs = []
        base_cost = 100
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            cost = base_cost + random.uniform(-20, 30)
            daily_costs.append({"date": date, "cost": round(cost, 2)})
        
        top_services = [
            ["EC2-Instance", round(random.uniform(800, 1200), 2)],
            ["S3", round(random.uniform(200, 400), 2)],
            ["RDS", round(random.uniform(300, 600), 2)],
            ["Lambda", round(random.uniform(50, 150), 2)],
            ["CloudFront", round(random.uniform(100, 300), 2)]
        ]
        
        return json.dumps({
            "total_cost": sum(service[1] for service in top_services),
            "daily_costs": daily_costs,
            "top_services": top_services,
            "cost_trend": "increasing" if random.random() > 0.5 else "decreasing",
            "period": time_period
        })

class EC2UtilizationTool:
    def _run(self) -> str:
        """Mock EC2 utilization data"""
        instance_types = ["t3.micro", "t3.small", "t3.medium", "m5.large", "c5.xlarge"]
        recommendations = ["Optimal", "Downsize", "Consider Reserved", "Terminate"]
        
        instances = []
        for i in range(4):
            instances.append({
                "instance_id": f"i-{random.randint(100000000000000000, 999999999999999999):016x}",
                "instance_type": random.choice(instance_types),
                "avg_cpu_utilization": round(random.uniform(15, 95), 1),
                "memory_utilization": round(random.uniform(20, 85), 1),
                "recommendation": random.choice(recommendations),
                "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
                "monthly_cost": round(random.uniform(20, 200), 2)
            })
        
        return json.dumps({
            "total_instances": len(instances),
            "instances": instances,
            "potential_monthly_savings": sum(random.uniform(10, 50) for _ in instances),
            "avg_utilization": round(sum(inst["avg_cpu_utilization"] for inst in instances) / len(instances), 1)
        })

class S3OptimizationTool:
    def _run(self) -> str:
        """Mock S3 optimization data"""
        buckets = [
            {
                "bucket_name": "data-backup-prod",
                "size_gb": 1024,
                "monthly_cost": 23.04,
                "storage_class": "Standard",
                "recommendations": ["Enable lifecycle policy", "Use IA for old data"]
            },
            {
                "bucket_name": "logs-archive",
                "size_gb": 2048,
                "monthly_cost": 46.08,
                "storage_class": "Standard",
                "recommendations": ["Use Glacier for archival", "Enable compression"]
            },
            {
                "bucket_name": "static-assets",
                "size_gb": 512,
                "monthly_cost": 11.52,
                "storage_class": "Standard-IA",
                "recommendations": ["Already optimized"]
            }
        ]
        
        return json.dumps({
            "total_buckets": len(buckets),
            "buckets": buckets,
            "total_size_gb": sum(bucket["size_gb"] for bucket in buckets),
            "total_monthly_cost": sum(bucket["monthly_cost"] for bucket in buckets)
        })