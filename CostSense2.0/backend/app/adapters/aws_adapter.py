from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
from .base import CloudCostProvider, CostData, ResourceData, UtilizationData, CloudProvider
from ..logging_config import get_logger

logger = get_logger(__name__)


class AWSCostAdapter(CloudCostProvider):
    """AWS Cost Explorer adapter"""

    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.session = None
        self.ce_client = None
        self.ec2_client = None
        self._initialize_clients()

    def get_provider_name(self) -> CloudProvider:
        return CloudProvider.AWS

    def _initialize_clients(self):
        """Initialize AWS clients"""
        try:
            self.session = boto3.Session(
                aws_access_key_id=self.credentials.get("aws_access_key_id"),
                aws_secret_access_key=self.credentials.get("aws_secret_access_key"),
                region_name=self.credentials.get("aws_region", "us-east-1"),
            )
            self.ce_client = self.session.client("ce")
            self.ec2_client = self.session.client("ec2")
            logger.info("AWS clients initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize AWS clients", error=str(e))
            raise

    async def fetch_costs(
        self,
        start_date: datetime,
        end_date: datetime,
        account_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[CostData]:
        """Fetch cost data from AWS Cost Explorer"""
        try:
            # Build the Cost Explorer query
            time_period = {
                "Start": start_date.strftime("%Y-%m-%d"),
                "End": end_date.strftime("%Y-%m-%d"),
            }

            # Request cost and usage data
            response = self.ce_client.get_cost_and_usage(
                TimePeriod=time_period,
                Granularity="DAILY",
                Metrics=["UnblendedCost"],
                GroupBy=[
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                    {"Type": "DIMENSION", "Key": "REGION"},
                ],
            )

            # Parse and normalize the response
            cost_records = []
            for result in response.get("ResultsByTime", []):
                period_start = datetime.strptime(result["TimePeriod"]["Start"], "%Y-%m-%d")
                period_end = datetime.strptime(result["TimePeriod"]["End"], "%Y-%m-%d")

                for group in result.get("Groups", []):
                    service = group["Keys"][0]
                    region = group["Keys"][1]
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])

                    if amount > 0:  # Only include non-zero costs
                        cost_data = CostData(
                            provider=CloudProvider.AWS,
                            account_id=account_id or "default",
                            resource_id=f"{service}:{region}",
                            resource_type=service,
                            resource_name=service,
                            region=region,
                            cost=amount,
                            currency="USD",
                            period_start=period_start,
                            period_end=period_end,
                            tags={},
                            metadata={"raw_service": service},
                        )
                        cost_records.append(cost_data)

            logger.info(
                "Fetched AWS costs",
                record_count=len(cost_records),
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
            )

            return cost_records

        except ClientError as e:
            logger.error("AWS Cost Explorer API error", error=str(e))
            raise
        except Exception as e:
            logger.error("Failed to fetch AWS costs", error=str(e))
            raise

    async def fetch_utilization(
        self,
        resource_id: str,
        metric_name: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[UtilizationData]:
        """Fetch utilization metrics from CloudWatch"""
        # Placeholder implementation
        logger.warning("AWS utilization fetching not yet implemented")
        return []

    async def list_resources(
        self,
        resource_type: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[ResourceData]:
        """List AWS resources (EC2 instances as example)"""
        try:
            resources = []

            # Example: List EC2 instances
            if not resource_type or resource_type.lower() == "ec2":
                response = self.ec2_client.describe_instances()

                for reservation in response.get("Reservations", []):
                    for instance in reservation.get("Instances", []):
                        tags_dict = {
                            tag["Key"]: tag["Value"]
                            for tag in instance.get("Tags", [])
                        }

                        resource = ResourceData(
                            provider=CloudProvider.AWS,
                            account_id=self.credentials.get("account_id", "default"),
                            resource_id=instance["InstanceId"],
                            resource_type="EC2Instance",
                            resource_name=tags_dict.get("Name", instance["InstanceId"]),
                            region=instance["Placement"]["AvailabilityZone"][:-1],
                            status=instance["State"]["Name"],
                            tags=tags_dict,
                            metadata={
                                "instance_type": instance["InstanceType"],
                                "launch_time": instance["LaunchTime"].isoformat(),
                            },
                        )
                        resources.append(resource)

            logger.info("Listed AWS resources", count=len(resources))
            return resources

        except ClientError as e:
            logger.error("AWS API error", error=str(e))
            raise
        except Exception as e:
            logger.error("Failed to list AWS resources", error=str(e))
            raise
