import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
from strands_tools import Tool
from src.config.settings import Settings

settings = Settings()

class AWSCostExplorerTool(Tool):
    def __init__(self):
        super().__init__(
            name="aws_cost_explorer",
            description="Retrieve AWS cost and usage data from Cost Explorer"
        )
    
    def _run(self, time_period: str = "30_days") -> str:
        try:
            # Initialize Cost Explorer client
            ce_client = boto3.client(
                'ce',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID if settings.AWS_ACCESS_KEY_ID else None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY if settings.AWS_SECRET_ACCESS_KEY else None
            )
            
            # Calculate date range
            end_date = datetime.now().date()
            if time_period == "7_days":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30_days":
                start_date = end_date - timedelta(days=30)
            elif time_period == "90_days":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get cost and usage data
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            # Process the response
            total_cost = 0
            daily_costs = []
            service_costs = {}
            
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                daily_total = float(result['Total']['BlendedCost']['Amount'])
                total_cost += daily_total
                
                daily_costs.append({
                    'date': date,
                    'cost': daily_total
                })
                
                # Service breakdown
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    if service in service_costs:
                        service_costs[service] += cost
                    else:
                        service_costs[service] = cost
            
            # Sort services by cost
            sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
            
            result_data = {
                "total_cost": round(total_cost, 2),
                "period": time_period,
                "daily_costs": daily_costs,
                "top_services": sorted_services[:10],
                "analysis_date": datetime.now().isoformat()
            }
            
            return json.dumps(result_data, indent=2)
            
        except Exception as e:
            return f"Error retrieving cost data: {str(e)}"

class EC2UtilizationTool(Tool):
    def __init__(self):
        super().__init__(
            name="ec2_utilization",
            description="Analyze EC2 instance utilization and optimization opportunities"
        )
    
    def _run(self, region: str = None) -> str:
        try:
            region = region or settings.AWS_REGION
            
            # Initialize EC2 and CloudWatch clients
            ec2_client = boto3.client(
                'ec2',
                region_name=region,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID if settings.AWS_ACCESS_KEY_ID else None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY if settings.AWS_SECRET_ACCESS_KEY else None
            )
            
            cloudwatch_client = boto3.client(
                'cloudwatch',
                region_name=region,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID if settings.AWS_ACCESS_KEY_ID else None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY if settings.AWS_SECRET_ACCESS_KEY else None
            )
            
            # Get running instances
            instances_response = ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            
            instances_data = []
            total_instances = 0
            
            for reservation in instances_response['Reservations']:
                for instance in reservation['Instances']:
                    total_instances += 1
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    
                    # Get CPU utilization
                    end_time = datetime.utcnow()
                    start_time = end_time - timedelta(days=7)
                    
                    cpu_response = cloudwatch_client.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=3600,
                        Statistics=['Average']
                    )
                    
                    avg_cpu = 0
                    if cpu_response['Datapoints']:
                        avg_cpu = sum(dp['Average'] for dp in cpu_response['Datapoints']) / len(cpu_response['Datapoints'])
                    
                    # Determine optimization recommendation
                    recommendation = "Optimal"
                    if avg_cpu < 10:
                        recommendation = "Consider downsizing or terminating"
                    elif avg_cpu < 25:
                        recommendation = "Consider smaller instance type"
                    elif avg_cpu > 80:
                        recommendation = "Consider larger instance type"
                    
                    instances_data.append({
                        'instance_id': instance_id,
                        'instance_type': instance_type,
                        'avg_cpu_utilization': round(avg_cpu, 2),
                        'recommendation': recommendation
                    })
            
            # Calculate potential savings
            underutilized = [i for i in instances_data if i['avg_cpu_utilization'] < 25]
            potential_savings = len(underutilized) * 50  # Rough estimate
            
            result_data = {
                "total_instances": total_instances,
                "region": region,
                "instances": instances_data,
                "underutilized_count": len(underutilized),
                "potential_monthly_savings": potential_savings,
                "analysis_date": datetime.now().isoformat()
            }
            
            return json.dumps(result_data, indent=2)
            
        except Exception as e:
            return f"Error analyzing EC2 utilization: {str(e)}"

class S3OptimizationTool(Tool):
    def __init__(self):
        super().__init__(
            name="s3_optimization",
            description="Analyze S3 storage costs and optimization opportunities"
        )
    
    def _run(self, bucket_limit: int = 20) -> str:
        try:
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID if settings.AWS_ACCESS_KEY_ID else None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY if settings.AWS_SECRET_ACCESS_KEY else None
            )
            
            # Get all buckets
            buckets_response = s3_client.list_buckets()
            
            buckets_data = []
            total_size = 0
            total_objects = 0
            
            for i, bucket in enumerate(buckets_response['Buckets'][:bucket_limit]):
                bucket_name = bucket['Name']
                
                try:
                    # Get bucket metrics
                    cloudwatch_client = boto3.client(
                        'cloudwatch',
                        region_name=settings.AWS_REGION,
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID if settings.AWS_ACCESS_KEY_ID else None,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY if settings.AWS_SECRET_ACCESS_KEY else None
                    )
                    
                    # Get bucket size
                    size_response = cloudwatch_client.get_metric_statistics(
                        Namespace='AWS/S3',
                        MetricName='BucketSizeBytes',
                        Dimensions=[
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': 'StandardStorage'}
                        ],
                        StartTime=datetime.utcnow() - timedelta(days=2),
                        EndTime=datetime.utcnow(),
                        Period=86400,
                        Statistics=['Average']
                    )
                    
                    bucket_size = 0
                    if size_response['Datapoints']:
                        bucket_size = size_response['Datapoints'][-1]['Average']
                    
                    # Get object count
                    objects_response = cloudwatch_client.get_metric_statistics(
                        Namespace='AWS/S3',
                        MetricName='NumberOfObjects',
                        Dimensions=[
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                        ],
                        StartTime=datetime.utcnow() - timedelta(days=2),
                        EndTime=datetime.utcnow(),
                        Period=86400,
                        Statistics=['Average']
                    )
                    
                    object_count = 0
                    if objects_response['Datapoints']:
                        object_count = int(objects_response['Datapoints'][-1]['Average'])
                    
                    total_size += bucket_size
                    total_objects += object_count
                    
                    # Generate recommendations
                    recommendations = []
                    if bucket_size > 1e12:  # > 1TB
                        recommendations.append("Consider Glacier for archival")
                    if object_count > 100000:
                        recommendations.append("Review object lifecycle policies")
                    
                    buckets_data.append({
                        'bucket_name': bucket_name,
                        'size_bytes': bucket_size,
                        'size_gb': round(bucket_size / (1024**3), 2),
                        'object_count': object_count,
                        'recommendations': recommendations
                    })
                    
                except Exception as bucket_error:
                    buckets_data.append({
                        'bucket_name': bucket_name,
                        'size_bytes': 0,
                        'size_gb': 0,
                        'object_count': 0,
                        'error': str(bucket_error),
                        'recommendations': ['Unable to analyze - check permissions']
                    })
            
            # Sort by size
            buckets_data.sort(key=lambda x: x['size_bytes'], reverse=True)
            
            # Calculate potential savings
            large_buckets = [b for b in buckets_data if b['size_gb'] > 100]
            potential_savings = len(large_buckets) * 20  # Rough estimate
            
            result_data = {
                "total_buckets_analyzed": len(buckets_data),
                "total_size_gb": round(total_size / (1024**3), 2),
                "total_objects": total_objects,
                "buckets": buckets_data,
                "large_buckets_count": len(large_buckets),
                "potential_monthly_savings": potential_savings,
                "analysis_date": datetime.now().isoformat()
            }
            
            return json.dumps(result_data, indent=2)
            
        except Exception as e:
            return f"Error analyzing S3 storage: {str(e)}"