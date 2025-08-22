import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ComponentRequest(BaseModel):
    name: str
    variant: Optional[str] = "default"
    props: Optional[Dict[str, Any]] = {}
    children: Optional[str] = None

class ComponentResponse(BaseModel):
    name: str
    code: str
    imports: List[str]
    dependencies: List[str]
    timestamp: str

class ShadcnMCPServer:
    def __init__(self):
        self.components_path = Path(__file__).parent.parent.parent.parent / "frontend" / "src" / "components" / "ui"
        self.available_components = self._load_available_components()
        
    def _load_available_components(self) -> Dict[str, Dict[str, Any]]:
        """Load available Shadcn UI components"""
        components = {
            "button": {
                "variants": ["default", "destructive", "outline", "secondary", "ghost", "link"],
                "sizes": ["default", "sm", "lg", "icon"],
                "dependencies": ["@radix-ui/react-slot", "class-variance-authority", "clsx", "tailwind-merge"],
                "imports": ["Button", "buttonVariants"]
            },
            "card": {
                "variants": ["default"],
                "dependencies": ["clsx", "tailwind-merge"],
                "imports": ["Card", "CardHeader", "CardFooter", "CardTitle", "CardDescription", "CardContent"]
            },
            "badge": {
                "variants": ["default", "secondary", "destructive", "outline", "success", "warning"],
                "dependencies": ["class-variance-authority", "clsx", "tailwind-merge"],
                "imports": ["Badge", "badgeVariants"]
            },
            "progress": {
                "variants": ["default"],
                "dependencies": ["@radix-ui/react-progress", "clsx", "tailwind-merge"],
                "imports": ["Progress"]
            },
            "alert": {
                "variants": ["default", "destructive", "warning", "success"],
                "dependencies": ["class-variance-authority", "clsx", "tailwind-merge"],
                "imports": ["Alert", "AlertTitle", "AlertDescription"]
            },
            "input": {
                "variants": ["default"],
                "dependencies": ["clsx", "tailwind-merge"],
                "imports": ["Input"]
            },
            "label": {
                "variants": ["default"],
                "dependencies": ["@radix-ui/react-label", "class-variance-authority", "clsx", "tailwind-merge"],
                "imports": ["Label"]
            },
            "select": {
                "variants": ["default"],
                "dependencies": ["@radix-ui/react-select", "clsx", "tailwind-merge"],
                "imports": ["Select", "SelectContent", "SelectItem", "SelectTrigger", "SelectValue"]
            },
            "dialog": {
                "variants": ["default"],
                "dependencies": ["@radix-ui/react-dialog", "clsx", "tailwind-merge"],
                "imports": ["Dialog", "DialogContent", "DialogDescription", "DialogHeader", "DialogTitle", "DialogTrigger"]
            },
            "dropdown-menu": {
                "variants": ["default"],
                "dependencies": ["@radix-ui/react-dropdown-menu", "clsx", "tailwind-merge"],
                "imports": ["DropdownMenu", "DropdownMenuContent", "DropdownMenuItem", "DropdownMenuLabel", "DropdownMenuSeparator", "DropdownMenuTrigger"]
            }
        }
        return components

    async def get_component(self, request: ComponentRequest) -> ComponentResponse:
        """Get a Shadcn UI component with specified configuration"""
        try:
            component_name = request.name.lower()
            
            if component_name not in self.available_components:
                raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
            
            component_info = self.available_components[component_name]
            
            # Generate component code based on request
            code = self._generate_component_code(request, component_info)
            
            return ComponentResponse(
                name=component_name,
                code=code,
                imports=component_info["imports"],
                dependencies=component_info.get("dependencies", []),
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating component {request.name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def _generate_component_code(self, request: ComponentRequest, component_info: Dict[str, Any]) -> str:
        """Generate component JSX code"""
        component_name = request.name.lower()
        variant = request.variant or "default"
        props = request.props or {}
        children = request.children or ""
        
        # Component-specific code generation
        if component_name == "button":
            return self._generate_button_code(variant, props, children)
        elif component_name == "card":
            return self._generate_card_code(props, children)
        elif component_name == "badge":
            return self._generate_badge_code(variant, props, children)
        elif component_name == "progress":
            return self._generate_progress_code(props)
        elif component_name == "alert":
            return self._generate_alert_code(variant, props, children)
        else:
            return self._generate_generic_code(component_name, variant, props, children)

    def _generate_button_code(self, variant: str, props: Dict[str, Any], children: str) -> str:
        """Generate Button component code"""
        props_str = self._format_props({**props, "variant": variant})
        return f'<Button{props_str}>{children or "Click me"}</Button>'

    def _generate_card_code(self, props: Dict[str, Any], children: str) -> str:
        """Generate Card component code"""
        props_str = self._format_props(props)
        
        if children:
            return f'<Card{props_str}>{children}</Card>'
        
        return f'''<Card{props_str}>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here.</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here.</p>
  </CardContent>
  <CardFooter>
    <p>Card footer</p>
  </CardFooter>
</Card>'''

    def _generate_badge_code(self, variant: str, props: Dict[str, Any], children: str) -> str:
        """Generate Badge component code"""
        props_str = self._format_props({**props, "variant": variant})
        return f'<Badge{props_str}>{children or "Badge"}</Badge>'

    def _generate_progress_code(self, props: Dict[str, Any]) -> str:
        """Generate Progress component code"""
        value = props.get("value", 50)
        props_str = self._format_props({**props, "value": value})
        return f'<Progress{props_str} />'

    def _generate_alert_code(self, variant: str, props: Dict[str, Any], children: str) -> str:
        """Generate Alert component code"""
        props_str = self._format_props({**props, "variant": variant})
        
        if children:
            return f'<Alert{props_str}>{children}</Alert>'
        
        return f'''<Alert{props_str}>
  <AlertTitle>Alert Title</AlertTitle>
  <AlertDescription>
    Alert description goes here.
  </AlertDescription>
</Alert>'''

    def _generate_generic_code(self, component_name: str, variant: str, props: Dict[str, Any], children: str) -> str:
        """Generate generic component code"""
        capitalized_name = component_name.capitalize()
        props_str = self._format_props({**props, "variant": variant} if variant != "default" else props)
        return f'<{capitalized_name}{props_str}>{children or f"{capitalized_name} content"}</{capitalized_name}>'

    def _format_props(self, props: Dict[str, Any]) -> str:
        """Format props as JSX attributes"""
        if not props:
            return ""
        
        formatted_props = []
        for key, value in props.items():
            if isinstance(value, bool):
                if value:
                    formatted_props.append(key)
            elif isinstance(value, str):
                formatted_props.append(f'{key}="{value}"')
            elif isinstance(value, (int, float)):
                formatted_props.append(f'{key}={{{value}}}')
            else:
                formatted_props.append(f'{key}={{{json.dumps(value)}}}')
        
        return " " + " ".join(formatted_props) if formatted_props else ""

    async def list_components(self) -> Dict[str, Any]:
        """List all available components"""
        return {
            "components": self.available_components,
            "total": len(self.available_components),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_component_variants(self, component_name: str) -> Dict[str, Any]:
        """Get available variants for a component"""
        component_name = component_name.lower()
        
        if component_name not in self.available_components:
            raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
        
        component_info = self.available_components[component_name]
        
        return {
            "component": component_name,
            "variants": component_info.get("variants", ["default"]),
            "sizes": component_info.get("sizes", []),
            "dependencies": component_info.get("dependencies", []),
            "imports": component_info.get("imports", []),
            "timestamp": datetime.utcnow().isoformat()
        }

# Global server instance
shadcn_server = ShadcnMCPServer()