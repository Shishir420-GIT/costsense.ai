from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from src.mcp.shadcn_server import shadcn_server, ComponentRequest, ComponentResponse

router = APIRouter()

@router.get("/components")
async def list_components() -> Dict[str, Any]:
    """List all available Shadcn UI components"""
    try:
        return await shadcn_server.list_components()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list components: {str(e)}")

@router.get("/components/{component_name}/variants")
async def get_component_variants(component_name: str) -> Dict[str, Any]:
    """Get available variants for a specific component"""
    try:
        return await shadcn_server.get_component_variants(component_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get variants: {str(e)}")

@router.post("/components/generate", response_model=ComponentResponse)
async def generate_component(request: ComponentRequest) -> ComponentResponse:
    """Generate a Shadcn UI component with specified configuration"""
    try:
        return await shadcn_server.get_component(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate component: {str(e)}")

@router.get("/components/{component_name}/template")
async def get_component_template(component_name: str, variant: str = "default") -> Dict[str, Any]:
    """Get a template for a specific component"""
    try:
        request = ComponentRequest(name=component_name, variant=variant)
        response = await shadcn_server.get_component(request)
        
        return {
            "component": component_name,
            "variant": variant,
            "template": response.code,
            "imports": response.imports,
            "dependencies": response.dependencies,
            "usage_example": f"""
import {{ {', '.join(response.imports)} }} from '@/components/ui/{component_name}'

export function Example() {{
  return (
    {response.code}
  )
}}""",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")

@router.post("/components/batch-generate")
async def batch_generate_components(requests: List[ComponentRequest]) -> List[ComponentResponse]:
    """Generate multiple components at once"""
    try:
        responses = []
        for request in requests:
            response = await shadcn_server.get_component(request)
            responses.append(response)
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to batch generate components: {str(e)}")

@router.get("/health")
async def mcp_health_check() -> Dict[str, Any]:
    """Health check for Shadcn MCP server"""
    return {
        "status": "healthy",
        "service": "shadcn-mcp-server",
        "version": "1.0.0",
        "components_available": len(shadcn_server.available_components),
        "timestamp": datetime.utcnow().isoformat()
    }