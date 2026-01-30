from typing import Callable, Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..logging_config import get_logger

logger = get_logger(__name__)


class FunctionParameter(BaseModel):
    """Function parameter definition"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class Function(BaseModel):
    """Function definition for LLM function calling"""
    name: str
    description: str
    parameters: List[FunctionParameter]
    handler: Optional[Callable] = Field(None, exclude=True)

    class Config:
        arbitrary_types_allowed = True


class FunctionRegistry:
    """Registry for LLM-callable functions"""

    _functions: Dict[str, Function] = {}

    @classmethod
    def register(cls, function: Function, handler: Callable):
        """Register a function with its handler"""
        function.handler = handler
        cls._functions[function.name] = function
        logger.info(f"Registered function: {function.name}")

    @classmethod
    def get_function(cls, name: str) -> Optional[Function]:
        """Get function by name"""
        return cls._functions.get(name)

    @classmethod
    def list_functions(cls) -> List[Function]:
        """List all registered functions"""
        return list(cls._functions.values())

    @classmethod
    def get_function_definitions(cls) -> List[Dict[str, Any]]:
        """Get function definitions for LLM"""
        return [
            {
                "name": func.name,
                "description": func.description,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "description": p.description,
                        "required": p.required,
                    }
                    for p in func.parameters
                ],
            }
            for func in cls._functions.values()
        ]

    @classmethod
    async def execute(cls, name: str, **kwargs) -> Any:
        """Execute a registered function"""
        function = cls.get_function(name)

        if not function:
            raise ValueError(f"Function not found: {name}")

        if not function.handler:
            raise ValueError(f"No handler registered for function: {name}")

        try:
            logger.info(f"Executing function: {name}", kwargs=kwargs)

            # Validate required parameters
            required_params = [p.name for p in function.parameters if p.required]
            missing = set(required_params) - set(kwargs.keys())

            if missing:
                raise ValueError(f"Missing required parameters: {missing}")

            # Execute the function
            if callable(function.handler):
                result = await function.handler(**kwargs)
            else:
                result = function.handler(**kwargs)

            logger.info(f"Function executed successfully: {name}")
            return result

        except Exception as e:
            logger.error(f"Function execution failed: {name}", error=str(e))
            raise


# Predefined functions for cost management
COST_QUERY_FUNCTION = Function(
    name="query_costs",
    description="Query cloud costs for a specific time period and filters",
    parameters=[
        FunctionParameter(
            name="provider",
            type="string",
            description="Cloud provider (aws, azure, gcp)",
            required=False,
        ),
        FunctionParameter(
            name="days",
            type="integer",
            description="Number of days to look back (default: 30)",
            required=False,
            default=30,
        ),
        FunctionParameter(
            name="resource_type",
            type="string",
            description="Filter by specific resource type",
            required=False,
        ),
    ],
)

OPTIMIZATION_FUNCTION = Function(
    name="analyze_optimization",
    description="Analyze costs and identify optimization opportunities",
    parameters=[
        FunctionParameter(
            name="provider",
            type="string",
            description="Cloud provider to analyze",
            required=False,
        ),
        FunctionParameter(
            name="threshold",
            type="number",
            description="Minimum cost threshold for recommendations",
            required=False,
            default=100.0,
        ),
    ],
)

CREATE_TICKET_FUNCTION = Function(
    name="create_ticket",
    description="Create a ServiceNow ticket for cost optimization",
    parameters=[
        FunctionParameter(
            name="title",
            type="string",
            description="Ticket title",
            required=True,
        ),
        FunctionParameter(
            name="description",
            type="string",
            description="Detailed description",
            required=True,
        ),
        FunctionParameter(
            name="priority",
            type="string",
            description="Ticket priority (low, medium, high, critical)",
            required=False,
            default="medium",
        ),
    ],
)
