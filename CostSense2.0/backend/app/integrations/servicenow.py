import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from ..config import settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class TicketPayload(BaseModel):
    """ServiceNow ticket payload"""
    title: str
    description: str
    priority: str = "medium"
    category: str = "cost_optimization"
    evidence: list[str] = []
    recommendations: list[str] = []
    estimated_savings: float = 0.0


class TicketResponse(BaseModel):
    """ServiceNow ticket creation response"""
    success: bool
    ticket_number: Optional[str] = None
    sys_id: Optional[str] = None
    ticket_url: Optional[str] = None
    error: Optional[str] = None


class ServiceNowClient:
    """Client for ServiceNow REST API"""

    def __init__(
        self,
        instance: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.instance = instance or settings.servicenow_instance
        self.username = username or settings.servicenow_username
        self.password = password or settings.servicenow_password

        self.enabled = bool(self.instance and self.username and self.password)

        if self.enabled:
            self.base_url = f"https://{self.instance}.service-now.com/api/now"
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                auth=(self.username, self.password),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=30.0,
            )
            logger.info("ServiceNow client initialized", instance=self.instance)
        else:
            logger.warning("ServiceNow credentials not configured - using mock mode")
            self.client = None

    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()

    async def create_incident(self, payload: TicketPayload) -> TicketResponse:
        """Create a ServiceNow incident ticket"""
        if not self.enabled:
            # Mock mode - return fake ticket
            return self._create_mock_ticket(payload)

        try:
            # Map priority to ServiceNow values
            priority_map = {
                "low": "4",
                "medium": "3",
                "high": "2",
                "critical": "1",
            }

            # Build incident payload
            incident_data = {
                "short_description": payload.title,
                "description": self._format_description(payload),
                "priority": priority_map.get(payload.priority.lower(), "3"),
                "category": payload.category,
                "impact": "2",  # Medium
                "urgency": "2",  # Medium
                "assignment_group": "Cloud Cost Optimization",
            }

            # Create incident
            response = await self.client.post(
                "/table/incident",
                json=incident_data,
            )
            response.raise_for_status()

            result = response.json().get("result", {})
            ticket_number = result.get("number")
            sys_id = result.get("sys_id")

            ticket_url = f"https://{self.instance}.service-now.com/nav_to.do?uri=incident.do?sys_id={sys_id}"

            logger.info(
                "ServiceNow incident created",
                ticket_number=ticket_number,
                sys_id=sys_id,
            )

            return TicketResponse(
                success=True,
                ticket_number=ticket_number,
                sys_id=sys_id,
                ticket_url=ticket_url,
            )

        except httpx.HTTPError as e:
            logger.error("ServiceNow API error", error=str(e))
            return TicketResponse(
                success=False,
                error=f"ServiceNow API error: {str(e)}",
            )
        except Exception as e:
            logger.error("Failed to create ServiceNow ticket", error=str(e))
            return TicketResponse(
                success=False,
                error=str(e),
            )

    def _format_description(self, payload: TicketPayload) -> str:
        """Format ticket description with evidence and recommendations"""
        description = f"{payload.description}\n\n"

        if payload.estimated_savings > 0:
            description += f"**Estimated Monthly Savings**: ${payload.estimated_savings:,.2f}\n\n"

        if payload.evidence:
            description += "**Evidence:**\n"
            for i, evidence in enumerate(payload.evidence, 1):
                description += f"{i}. {evidence}\n"
            description += "\n"

        if payload.recommendations:
            description += "**Recommended Actions:**\n"
            for i, rec in enumerate(payload.recommendations, 1):
                description += f"{i}. {rec}\n"
            description += "\n"

        description += f"\n---\nGenerated by CostSense AI on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"

        return description

    def _create_mock_ticket(self, payload: TicketPayload) -> TicketResponse:
        """Create mock ticket for testing without ServiceNow"""
        ticket_number = f"INC{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        sys_id = f"mock-{ticket_number.lower()}"

        logger.info(
            "Mock ticket created (ServiceNow not configured)",
            ticket_number=ticket_number,
            title=payload.title,
        )

        return TicketResponse(
            success=True,
            ticket_number=ticket_number,
            sys_id=sys_id,
            ticket_url=f"https://mock.service-now.com/incident/{sys_id}",
        )

    async def get_incident(self, sys_id: str) -> Optional[Dict[str, Any]]:
        """Get incident details by sys_id"""
        if not self.enabled:
            return {"number": "MOCK123", "state": "New", "sys_id": sys_id}

        try:
            response = await self.client.get(f"/table/incident/{sys_id}")
            response.raise_for_status()
            return response.json().get("result")

        except Exception as e:
            logger.error("Failed to get incident", sys_id=sys_id, error=str(e))
            return None

    async def update_incident(
        self, sys_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Update an existing incident"""
        if not self.enabled:
            logger.info("Mock incident update", sys_id=sys_id)
            return True

        try:
            response = await self.client.patch(
                f"/table/incident/{sys_id}",
                json=updates,
            )
            response.raise_for_status()

            logger.info("Incident updated", sys_id=sys_id)
            return True

        except Exception as e:
            logger.error("Failed to update incident", sys_id=sys_id, error=str(e))
            return False


# Global client instance
_servicenow_client: Optional[ServiceNowClient] = None


def get_servicenow_client() -> ServiceNowClient:
    """Get or create ServiceNow client"""
    global _servicenow_client
    if _servicenow_client is None:
        _servicenow_client = ServiceNowClient()
    return _servicenow_client
