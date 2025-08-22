import json
from typing import Dict, Any, List
from strands_tools import Tool
import pandas as pd

class SavingsCalculationTool(Tool):
    def __init__(self):
        super().__init__(
            name="savings_calculator",
            description="Calculate potential cost savings and ROI for optimization recommendations"
        )
    
    def _run(self, optimization_data: str) -> str:
        try:
            # Parse the optimization data
            if isinstance(optimization_data, str):
                data = json.loads(optimization_data)
            else:
                data = optimization_data
            
            total_potential_savings = 0
            detailed_calculations = []
            
            # EC2 Savings Calculations
            if 'ec2_data' in data:
                ec2_savings = self._calculate_ec2_savings(data['ec2_data'])
                total_potential_savings += ec2_savings['total_monthly_savings']
                detailed_calculations.append(ec2_savings)
            
            # S3 Savings Calculations
            if 's3_data' in data:
                s3_savings = self._calculate_s3_savings(data['s3_data'])
                total_potential_savings += s3_savings['total_monthly_savings']
                detailed_calculations.append(s3_savings)
            
            # RDS Savings Calculations
            if 'rds_data' in data:
                rds_savings = self._calculate_rds_savings(data['rds_data'])
                total_potential_savings += rds_savings['total_monthly_savings']
                detailed_calculations.append(rds_savings)
            
            # Calculate annual projections
            annual_savings = total_potential_savings * 12
            
            # Generate ROI analysis
            roi_analysis = self._calculate_roi_analysis(total_potential_savings, annual_savings)
            
            result = {
                "summary": {
                    "total_monthly_savings": round(total_potential_savings, 2),
                    "total_annual_savings": round(annual_savings, 2),
                    "confidence_level": self._calculate_confidence_level(detailed_calculations)
                },
                "detailed_calculations": detailed_calculations,
                "roi_analysis": roi_analysis,
                "recommendations": self._generate_priority_recommendations(detailed_calculations),
                "calculation_date": pd.Timestamp.now().isoformat()
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error calculating savings: {str(e)}"
    
    def _calculate_ec2_savings(self, ec2_data: Dict[str, Any]) -> Dict[str, Any]:
        total_savings = 0
        instance_recommendations = []
        
        for instance in ec2_data.get('instances', []):
            cpu_util = instance.get('avg_cpu_utilization', 0)
            instance_type = instance.get('instance_type', '')
            
            # Estimate current monthly cost based on instance type
            estimated_cost = self._estimate_ec2_cost(instance_type)
            
            savings = 0
            action = "No action needed"
            
            if cpu_util < 10:
                savings = estimated_cost * 0.8  # 80% savings if terminated
                action = "Consider termination"
            elif cpu_util < 25:
                savings = estimated_cost * 0.3  # 30% savings with smaller instance
                action = "Downsize instance"
            elif cpu_util < 50:
                savings = estimated_cost * 0.15  # 15% savings with optimization
                action = "Optimize configuration"
            
            total_savings += savings
            
            instance_recommendations.append({
                "instance_id": instance.get('instance_id'),
                "current_cost": estimated_cost,
                "potential_savings": round(savings, 2),
                "action": action,
                "cpu_utilization": cpu_util
            })
        
        return {
            "service": "EC2",
            "total_monthly_savings": round(total_savings, 2),
            "instance_count": len(ec2_data.get('instances', [])),
            "recommendations": instance_recommendations
        }
    
    def _calculate_s3_savings(self, s3_data: Dict[str, Any]) -> Dict[str, Any]:
        total_savings = 0
        bucket_recommendations = []
        
        for bucket in s3_data.get('buckets', []):
            size_gb = bucket.get('size_gb', 0)
            object_count = bucket.get('object_count', 0)
            
            # Standard storage cost: ~$0.023 per GB
            current_cost = size_gb * 0.023
            
            savings = 0
            actions = []
            
            # Lifecycle policies
            if object_count > 10000:
                lifecycle_savings = current_cost * 0.2
                savings += lifecycle_savings
                actions.append(f"Lifecycle policies: ${lifecycle_savings:.2f}")
            
            # Glacier archival for large buckets
            if size_gb > 100:
                glacier_savings = current_cost * 0.7
                savings += glacier_savings
                actions.append(f"Glacier archival: ${glacier_savings:.2f}")
            
            # Intelligent tiering
            if size_gb > 10:
                tiering_savings = current_cost * 0.15
                savings += tiering_savings
                actions.append(f"Intelligent tiering: ${tiering_savings:.2f}")
            
            total_savings += savings
            
            bucket_recommendations.append({
                "bucket_name": bucket.get('bucket_name'),
                "current_monthly_cost": round(current_cost, 2),
                "potential_savings": round(savings, 2),
                "actions": actions,
                "size_gb": size_gb
            })
        
        return {
            "service": "S3",
            "total_monthly_savings": round(total_savings, 2),
            "bucket_count": len(s3_data.get('buckets', [])),
            "recommendations": bucket_recommendations
        }
    
    def _calculate_rds_savings(self, rds_data: Dict[str, Any]) -> Dict[str, Any]:
        total_savings = 0
        db_recommendations = []
        
        for db in rds_data.get('databases', []):
            db_class = db.get('db_instance_class', '')
            cpu_util = db.get('avg_cpu_utilization', 0)
            
            # Estimate RDS cost based on instance class
            estimated_cost = self._estimate_rds_cost(db_class)
            
            savings = 0
            actions = []
            
            if cpu_util < 20:
                downsize_savings = estimated_cost * 0.4
                savings += downsize_savings
                actions.append(f"Downsize instance: ${downsize_savings:.2f}")
            
            # Reserved instance savings
            ri_savings = estimated_cost * 0.3
            savings += ri_savings
            actions.append(f"Reserved instances: ${ri_savings:.2f}")
            
            total_savings += savings
            
            db_recommendations.append({
                "db_identifier": db.get('db_instance_identifier'),
                "current_monthly_cost": estimated_cost,
                "potential_savings": round(savings, 2),
                "actions": actions,
                "cpu_utilization": cpu_util
            })
        
        return {
            "service": "RDS",
            "total_monthly_savings": round(total_savings, 2),
            "database_count": len(rds_data.get('databases', [])),
            "recommendations": db_recommendations
        }
    
    def _estimate_ec2_cost(self, instance_type: str) -> float:
        # Simplified cost estimation based on instance type
        cost_map = {
            't2.micro': 8.5, 't2.small': 17, 't2.medium': 34, 't2.large': 67,
            't3.micro': 7.5, 't3.small': 15, 't3.medium': 30, 't3.large': 60,
            'm5.large': 70, 'm5.xlarge': 140, 'm5.2xlarge': 280,
            'c5.large': 62, 'c5.xlarge': 124, 'c5.2xlarge': 248,
            'r5.large': 91, 'r5.xlarge': 182, 'r5.2xlarge': 364
        }
        return cost_map.get(instance_type, 50)  # Default estimate
    
    def _estimate_rds_cost(self, db_class: str) -> float:
        # Simplified RDS cost estimation
        cost_map = {
            'db.t2.micro': 15, 'db.t2.small': 30, 'db.t2.medium': 60,
            'db.t3.micro': 14, 'db.t3.small': 28, 'db.t3.medium': 56,
            'db.m5.large': 130, 'db.m5.xlarge': 260, 'db.m5.2xlarge': 520,
            'db.r5.large': 180, 'db.r5.xlarge': 360, 'db.r5.2xlarge': 720
        }
        return cost_map.get(db_class, 100)  # Default estimate
    
    def _calculate_roi_analysis(self, monthly_savings: float, annual_savings: float) -> Dict[str, Any]:
        # Assume implementation cost of 10% of first year savings
        implementation_cost = annual_savings * 0.1
        
        # Calculate payback period in months
        payback_months = implementation_cost / monthly_savings if monthly_savings > 0 else 0
        
        # 3-year ROI calculation
        three_year_savings = annual_savings * 3
        roi_percentage = ((three_year_savings - implementation_cost) / implementation_cost * 100) if implementation_cost > 0 else 0
        
        return {
            "implementation_cost": round(implementation_cost, 2),
            "payback_period_months": round(payback_months, 1),
            "three_year_savings": round(three_year_savings, 2),
            "three_year_roi_percentage": round(roi_percentage, 1)
        }
    
    def _calculate_confidence_level(self, calculations: List[Dict[str, Any]]) -> str:
        # Simple confidence calculation based on data availability
        total_recommendations = sum(len(calc.get('recommendations', [])) for calc in calculations)
        
        if total_recommendations > 10:
            return "High"
        elif total_recommendations > 5:
            return "Medium"
        else:
            return "Low"
    
    def _generate_priority_recommendations(self, calculations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_recommendations = []
        
        for calc in calculations:
            service = calc.get('service', 'Unknown')
            for rec in calc.get('recommendations', []):
                if isinstance(rec, dict) and rec.get('potential_savings', 0) > 0:
                    all_recommendations.append({
                        "service": service,
                        "priority": self._calculate_priority(rec.get('potential_savings', 0)),
                        "savings": rec.get('potential_savings', 0),
                        "description": rec.get('action', 'Optimize resource'),
                        "resource": rec.get('instance_id') or rec.get('bucket_name') or rec.get('db_identifier', 'Unknown')
                    })
        
        # Sort by savings amount
        all_recommendations.sort(key=lambda x: x['savings'], reverse=True)
        
        return all_recommendations[:10]  # Top 10 recommendations
    
    def _calculate_priority(self, savings: float) -> str:
        if savings > 100:
            return "High"
        elif savings > 50:
            return "Medium"
        else:
            return "Low"